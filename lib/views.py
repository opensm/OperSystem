from rest_framework.views import APIView
from lib.mixins import DataQueryPermission
from lib.response import DataResponse
from lib.page import RewritePageNumberPagination
from Rbac.serializers import MenuSerializer
from itertools import chain
from lib.exceptions import *


class BaseGETVIEW(DataQueryPermission, APIView, RewritePageNumberPagination):
    serializer_class = None

    def get(self, request):
        self.error_message = []
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        try:
            model_obj = self.get_user_data_objects(request=request)
            if not model_obj:
                raise APIException(
                    detail="获取数据失败！",
                    code=API_12001_DATA_NULL_ERROR
                )
            # if self.error_message:
            #     for x in self.error_message:
            #         print(x.default_detail)
            #         raise APIException(detail=x.default_detail, code=x.status_code)
        except APIException as error:
            return DataResponse(
                code=error.status_code,
                msg=error.default_detail
            )
        page_obj = self.paginate_queryset(queryset=model_obj, request=request, view=self)
        data = self.serializer_class(
            instance=page_obj,
            many=True
        )
        return self.get_paginated_response(
            data=data.data,
            msg="获取数据成功",
            code=API_00000_OK
        )


class BasePOSTVIEW(DataQueryPermission, APIView, RewritePageNumberPagination):
    serializer_class = None

    def post(self, request):
        self.error_message = []
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        data = self.serializer_class(
            data=request.data
        )
        if not data.is_valid():
            self.error_message.append(
                APIException(
                    detail="序列化数据出现异常，请检查输入参数！"
                )
            )
        try:
            if self.error_message:
                for x in self.error_message:
                    raise APIException(detail=x.default_detail, code=x.status_code)
        except APIException as error:
            return DataResponse(
                code=error.status_code,
                msg=error.default_detail
            )
        data.save()
        return DataResponse(
            data=data.data,
            msg='数据保存成功！',
            code=API_00000_OK
        )


class BaseDELETEVIEW(DataQueryPermission, APIView, RewritePageNumberPagination):
    serializer_class = None
    pk = None

    def delete(self, request):
        self.error_message = []
        model_obj = self.get_user_data_objects(request=request)
        if not model_obj:
            self.error_message.append(
                APIException(
                    detail="获取删除数据失败！",
                    code=API_12001_DATA_NULL_ERROR
                )
            )
        if not self.check_user_permissions(request=request):
            self.error_message.append(
                APIException(
                    detail="没有删除权限！！",
                    code=API_40003_PERMISSION_DENIED
                )
            )
        try:
            model_obj.delete()
            if self.error_message:
                for x in self.error_message:
                    raise APIException(detail=x.default_detail, code=x.status_code)
        except APIException as error:
            return DataResponse(
                code=error.status_code,
                msg=error.default_detail
            )

        return DataResponse(
            code=API_00000_OK,
            msg="删除信息成功!"
        )


class BasePUTVIEW(DataQueryPermission, APIView, RewritePageNumberPagination):
    serializer_class = None
    pk = None

    def put(self, request):
        """
        :param request:
        :return:
        """
        self.error_message = []
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        if not self.check_user_permissions(request=request):
            self.error_message.append(
                APIException(
                    detail="没有删除权限！！",
                    code=API_40003_PERMISSION_DENIED
                )
            )
        model_objs = self.get_user_data_objects(request=request)
        if not model_objs:
            self.error_message.append(
                APIException(detail="没获取到修改数据", code=API_12001_DATA_NULL_ERROR)
            )
        data = self.serializer_class(
            instance=model_objs,
            many=True,
            data=request.data
        )
        if not data.is_valid():
            self.error_message.append(
                APIException(detail="修改数据格式不匹配！", code=API_10001_PARAMS_ERROR)
            )
        try:
            for x in self.error_message:
                raise APIException(code=x.status_code, detail=x.default_detail)
            data.save()
            return DataResponse(msg="数据保存成功", code=API_00000_OK)
        except APIException as error:
            return DataResponse(
                data=request.data,
                msg="数据保存失败:%s" % error.default_detail,
                code=error.status_code
            )


class BaseListView(BaseGETVIEW, BasePOSTVIEW):
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

    # def get(self, request):
    #     if not self.serializer_class:
    #         raise TypeError("serializer_class type error!")
    #     model_obj = self.get_user_data_objects(request=request)
    #     if not model_obj:
    #         self.error_message.append(
    #             APIException(
    #                 detail="获取数据失败！",
    #                 code=API_12001_DATA_NULL_ERROR
    #             )
    #         )
    #     try:
    #         if self.error_message:
    #             for x in self.error_message:
    #                 raise APIException(detail=x.default_detail, code=x.default_code)
    #     except APIException as error:
    #         return DataResponse(
    #             code=error.status_code,
    #             msg=error.default_detail
    #         )
    #     page_obj = self.paginate_queryset(queryset=model_obj, request=request, view=self)
    #     data = self.serializer_class(
    #         instance=page_obj,
    #         many=True
    #     )
    #     return self.get_paginated_response(
    #         data=data.data,
    #         msg="获取数据成功",
    #         code=API_00000_OK
    #     )
    #
    # def post(self, request):
    #     if not self.serializer_class:
    #         raise TypeError("serializer_class type error!")
    #     data = self.serializer_class(
    #         data=request.data
    #     )
    #     if not data.is_valid():
    #         self.error_message.append(
    #             APIException(
    #                 detail="序列化数据出现异常，请检查输入参数！"
    #             )
    #         )
    #     try:
    #         if self.error_message:
    #             for x in self.error_message:
    #                 raise APIException(detail=x.default_detail, code=x.default_code)
    #     except APIException as error:
    #         return DataResponse(
    #             code=error.status_code,
    #             msg=error.default_detail
    #         )
    #     data.save()
    #     return DataResponse(
    #         data=data.data,
    #         msg='数据保存成功！',
    #         code=API_00000_OK
    #     )


# class BaseDetailView(DataQueryPermission, APIView, RewritePageNumberPagination):
class BaseDetailView(BaseDELETEVIEW, BasePUTVIEW, BaseGETVIEW):
    serializer_class = None
    pk = None

    def get_user_data_objects(self, request):
        self.kwargs = getattr(request, request.method)
        if self.pk is None:
            raise ValueError("pk 没有定义！")
        if self.pk not in self.kwargs:
            self.error_message.append(
                APIException(
                    detail="传入参数错误！",
                    code=API_10001_PARAMS_ERROR
                )
            )
        if self.page_size_query_param in self.kwargs:
            self.kwargs.pop(self.page_size_query_param)
        if self.page_query_param in self.kwargs:
            self.kwargs.pop(self.page_query_param)
        if self.sort_query_param in self.kwargs:
            self.kwargs.pop(self.sort_query_param)
        return super().get_user_data_objects(request)

    # def delete(self, request):
    #     model_obj = self.get_user_data_objects(request=request)
    #     if not model_obj:
    #         self.error_message.append(
    #             APIException(
    #                 detail="获取删除数据失败！",
    #                 code=API_12001_DATA_NULL_ERROR
    #             )
    #         )
    #     if not self.check_user_permissions(request=request):
    #         self.error_message.append(
    #             APIException(
    #                 detail="没有删除权限！！",
    #                 code=API_40003_PERMISSION_DENIED
    #             )
    #         )
    #     try:
    #         model_obj.delete()
    #         if self.error_message:
    #             for x in self.error_message:
    #                 raise APIException(detail=x.default_detail, code=x.default_code)
    #     except APIException as error:
    #         return DataResponse(
    #             code=error.status_code,
    #             msg=error.default_detail
    #         )
    #
    #     return DataResponse(
    #         code=API_00000_OK,
    #         msg="删除信息成功!"
    #     )
    #
    # def put(self, request):
    #     """
    #     :param request:
    #     :return:
    #     """
    #     if not self.serializer_class:
    #         raise TypeError("serializer_class type error!")
    #     if not self.check_user_permissions(request=request):
    #         self.error_message.append(
    #             APIException(
    #                 detail="没有删除权限！！",
    #                 code=API_40003_PERMISSION_DENIED
    #             )
    #         )
    #     model_objs = self.get_user_data_objects(request=request)
    #     data = self.serializer_class(
    #         instance=model_objs,
    #         many=True,
    #         data=request.data
    #     )
    #     if not data.is_valid():
    #         return DataResponse(data=request.data, msg="数据输入格式不匹配:{0}".format(data.errors), code="00001")
    #     try:
    #         data.save()
    #         return DataResponse(msg="数据保存成功", code="00000")
    #     except Exception as error:
    #         return DataResponse(
    #             data=request.data,
    #             msg="数据保存失败:%s" % error,
    #             code="00001"
    #         )
    #
    # def get(self, request):
    #     if not self.serializer_class:
    #         raise TypeError("serializer_class type error!")
    #     model_obj = self.get_user_data_objects(request=request)
    #     if not model_obj:
    #         return DataResponse(
    #             data=[],
    #             msg="获取数据失败",
    #             code="00001"
    #         )
    #     page_obj = self.paginate_queryset(queryset=model_obj, request=request, view=self)
    #     data = self.serializer_class(
    #         instance=page_obj,
    #         many=True
    #     )
    #     return self.get_paginated_response(
    #         data=data.data,
    #         msg="获取数据成功",
    #         code="00000"
    #     )


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


class BaseGetPUTView(BaseGETVIEW, BasePUTVIEW):
    serializer_class = None
    pk = None

    def get_user_data_objects(self, request):
        self.kwargs = getattr(request, request.method)
        if self.pk is None or self.pk not in self.kwargs:
            self.error_message.append(
                APIException(
                    detail="传入参数错误！",
                    code=API_10001_PARAMS_ERROR
                )
            )
        if self.page_size_query_param in self.kwargs:
            self.kwargs.pop(self.page_size_query_param)
        if self.page_query_param in self.kwargs:
            self.kwargs.pop(self.page_query_param)
        if self.sort_query_param in self.kwargs:
            self.kwargs.pop(self.sort_query_param)
        return super().get_user_data_objects(request)

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


class BasePUTView(BasePUTVIEW):
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
