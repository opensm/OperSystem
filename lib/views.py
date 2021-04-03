from rest_framework.views import APIView
from lib.mixins import DataQueryPermission
from lib.response import DataResponse
from lib.page import RewritePageNumberPagination
from Rbac.serializers import MenuSerializer
from itertools import chain


class BaseListView(DataQueryPermission, APIView, RewritePageNumberPagination):
    """A base view for displaying a single object."""
    serializer_class = None

    def get_user_data_objects(self, request):
        if self.page_size_query_param in self.kwargs:
            self.kwargs.pop(self.page_size_query_param)
        if self.page_query_param in self.kwargs:
            self.kwargs.pop(self.page_query_param)
        if self.sort_query_param in self.kwargs:
            self.kwargs.pop(self.sort_query_param)
        return super().get_user_data_objects(request)

    def get(self, request):
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        model_obj = self.get_user_data_objects(request=request)
        if not model_obj:
            return DataResponse(
                code="00001",
                msg="删除数据异常，获取到删除数据失败！"
            )
        page_obj = self.paginate_queryset(queryset=model_obj, request=request, view=self)
        data = self.serializer_class(
            instance=page_obj,
            many=True
        )
        return self.get_paginated_response(
            data=data.data,
            msg="获取数据成功",
            code="00000"
        )

    def post(self, request):
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        data = self.serializer_class(
            data=request.data
        )
        if not data.is_valid():
            return DataResponse(
                msg="添加参数异常",
                code='00001'
            )
        else:
            data.save()
            return DataResponse(
                data=data.data,
                msg='数据保存成功！',
                code='00000'
            )


class BaseDetailView(DataQueryPermission, APIView, RewritePageNumberPagination):
    serializer_class = None
    pk = None

    def get_user_data_objects(self, request):
        self.kwargs = getattr(request, request.method)
        print(self.kwargs)
        print(self.pk)
        if self.pk is None or self.pk not in self.kwargs:
            raise ValueError("没获取到pk")
        if self.page_size_query_param in self.kwargs:
            self.kwargs.pop(self.page_size_query_param)
        if self.page_query_param in self.kwargs:
            self.kwargs.pop(self.page_query_param)
        if self.sort_query_param in self.kwargs:
            self.kwargs.pop(self.sort_query_param)
        return super().get_user_data_objects(request)

    def delete(self, request):
        model_obj = self.get_user_data_objects(request=request)
        if not model_obj:
            return DataResponse(
                code="00001",
                msg="删除数据异常，获取到删除数据失败！"
            )
        if not self.check_user_permissions(request=request):
            return DataResponse(
                code="00001",
                msg=self.error_message
            )
        else:
            return DataResponse(
                code="00000",
                msg="删除信息成功!"
            )

    def put(self, request):
        """
        :param request:
        :return:
        """
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        if not self.check_user_permissions(request=request):
            return DataResponse(
                code="00001",
                msg=self.error_message
            )
        model_objs = self.get_user_data_objects(request=request)
        data = self.serializer_class(
            instance=model_objs,
            many=True,
            data=request.data
        )
        if not data.is_valid():
            return DataResponse(data=request.data, msg="数据输入格式不匹配:{0}".format(data.errors), code="00001")
        try:
            data.save()
            return DataResponse(msg="数据保存成功", code="00000")
        except Exception as error:
            return DataResponse(
                data=request.data,
                msg="数据保存失败:%s" % error,
                code="00001"
            )

    def get(self, request):
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        model_obj = self.get_user_data_objects(request=request)
        print(model_obj)
        if not model_obj:
            return DataResponse(
                data=[],
                msg="获取数据失败",
                code="00001"
            )
        page_obj = self.paginate_queryset(queryset=model_obj, request=request, view=self)
        data = self.serializer_class(
            instance=page_obj,
            many=True
        )
        return self.get_paginated_response(
            data=data.data,
            msg="获取数据成功",
            code="00000"
        )


class BaseGETView(DataQueryPermission, APIView):
    serializer_class = None
    pk = None

    def get(self, request):
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        model_obj = self.get_user_data_objects(request=request)
        data = self.serializer_class(
            instance=model_obj
        )
        return DataResponse(
            data=data.data,
            msg="获取信息成功！",
            code='00000'
        )


class UserGETView(DataQueryPermission, APIView):
    serializer_class = None
    pk = None

    def get_menu(self):
        """
        :return:
        """
        # 判断传入参数类型
        if not isinstance(self.user, self.get_user_model):
            raise TypeError("传入的用户类型错误！")
        # 超级用户直接返回全部权限
        # instance = self.get_user_model_data_permission()
        instance = list()
        for x in self.user.roles.all():
            instance = chain(x.menu.all(), instance)
        data = MenuSerializer(many=True, instance=instance)
        return data.data

    def get(self, request):
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        model_obj = self.get_user_data_objects(request=request)
        data = self.serializer_class(
            instance=model_obj
        )
        menu = data.data
        menu['user_permissions'] = self.get_menu()
        return DataResponse(
            data=data.data,
            msg="获取信息成功！",
            code='00000'
        )


class BaseGetPUTView(DataQueryPermission, APIView):
    serializer_class = None
    pk = None

    def put(self, request):
        """
        :param request:
        :return:
        """
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        if not self.check_user_permissions(request=request):
            return DataResponse(
                code="00001",
                msg=self.error_message
            )
        model_objs = self.get_user_data_objects(request=request)
        data = self.serializer_class(
            instance=model_objs,
            many=True,
            data=request.data
        )
        if not data.is_valid():
            return DataResponse(
                data=request.data,
                msg="数据输入格式不匹配:{0}".format(data.errors),
                code="00001"
            )
        try:
            data.save()
            return DataResponse(msg="数据保存成功", code="00000")
        except Exception as error:
            return DataResponse(
                data=request.data,
                msg="数据保存失败:%s" % error,
                code="00001"
            )

    def get(self, request):
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        model_obj = self.get_user_data_objects(request=request)
        data = self.serializer_class(
            instance=model_obj,
            many=True
        )
        return DataResponse(
            data=data.data,
            msg="获取信息成功",
            code="00000"
        )


class BasePUTView(DataQueryPermission, APIView):
    serializer_class = None
    pk = None

    def put(self, request):
        """
        :param request:
        :return:
        """
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        if not self.check_user_permissions(request=request):
            return DataResponse(
                code="00001",
                msg=self.error_message
            )
        model_objs = self.get_user_data_objects(request=request)
        data = self.serializer_class(
            instance=model_objs,
            many=True,
            data=request.data
        )
        if not data.is_valid():
            return DataResponse(
                data=request.data,
                msg="数据输入格式不匹配:{0}".format(data.errors),
                code="00001"
            )
        try:
            data.save()
            return DataResponse(msg="数据保存成功", code="00000")
        except Exception as error:
            return DataResponse(
                data=request.data,
                msg="数据保存失败:%s" % error,
                code="00001"
            )
