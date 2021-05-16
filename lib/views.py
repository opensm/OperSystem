from rest_framework.views import APIView
from lib.mixins import DataQueryPermission
from lib.response import DataResponse
from lib.page import RewritePageNumberPagination
from Rbac.serializers import MenuSerializer
from Rbac.models import Menu
from itertools import chain
from lib.exceptions import *
from lib.Log import RecodeLog
from django.apps import apps as django_apps


class BaseGETVIEW(DataQueryPermission, APIView, RewritePageNumberPagination):
    serializer_class = None

    def get(self, request):
        self.error_message = []
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        try:
            if not self.check_user_permissions(request=request):
                raise APIException(
                    detail="没有相关权限！",
                    code=API_40003_PERMISSION_DENIED
                )
            model_obj = self.get_user_data_objects(request=request)
            if not model_obj:
                raise APIException(
                    detail="获取数据失败！",
                    code=API_12001_DATA_NULL_ERROR
                )
            page_obj = self.paginate_queryset(queryset=model_obj, request=request, view=self)
            data = self.serializer_class(
                instance=page_obj,
                many=True
            )

            format_data = self.format_return_data(data=data.data)
            tag = self.check_user_post_permissions(request=request)
            return self.get_paginated_response(
                data=format_data,
                msg="获取数据成功",
                post=tag,
                code=API_00000_OK
            )
        except APIException as error:
            RecodeLog.error(msg="返回状态码:{1},错误信息:{0}".format(error.default_detail, error.status_code))
            return DataResponse(
                code=error.status_code,
                msg=error.default_detail
            )


class BasePOSTVIEW(DataQueryPermission, APIView, RewritePageNumberPagination):
    serializer_class = None

    def post(self, request):
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        try:
            data = self.serializer_class(
                data=request.data
            )
            if not self.check_user_method_permissions(request=request):
                raise APIException(
                    code=API_40003_PERMISSION_DENIED,
                    detail="没有权限操作"
                )
            if not data.is_valid():
                RecodeLog.error(msg="数据验证错误:{0}".format(data.errors))
                raise APIException(
                    detail="序列化数据出现异常，请检查输入参数！",
                    code=API_10001_PARAMS_ERROR,
                )
            data.save()
            return DataResponse(
                data=data.data,
                msg='数据保存成功！',
                code=API_00000_OK
            )
        except APIException as error:
            RecodeLog.error(msg="返回状态码:{1},错误信息:{0}".format(error.default_detail, error.status_code))
            return DataResponse(
                code=error.status_code,
                msg=error.default_detail
            )


class BaseDELETEVIEW(DataQueryPermission, APIView, RewritePageNumberPagination):
    serializer_class = None
    pk = None

    def delete(self, request):
        try:
            model_obj = self.get_user_data_objects(request=request)
            if not model_obj:
                raise APIException(
                    detail="获取删除数据失败！",
                    code=API_12001_DATA_NULL_ERROR
                )
            if not self.check_user_permissions(request=request):
                raise APIException(
                    detail="没有删除权限！！",
                    code=API_40003_PERMISSION_DENIED
                )
            model_obj.delete()
            return DataResponse(
                code=API_00000_OK,
                msg="删除信息成功!"
            )
        except APIException as error:
            RecodeLog.error(msg="返回状态码:{1},错误信息:{0}".format(error.default_detail, error.status_code))
            return DataResponse(
                code=error.status_code,
                msg=error.default_detail
            )


class BasePUTVIEW(DataQueryPermission, APIView, RewritePageNumberPagination):
    serializer_class = None
    pk = None

    def put(self, request):
        """
        :param request:
        :return:
        """
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        try:
            if not self.check_user_permissions(request=request):
                raise APIException(
                    detail="没有删除权限！！",
                    code=API_40003_PERMISSION_DENIED
                )
            model_objs = self.get_user_data_objects(request=request)
            if not model_objs or len(model_objs) > 1:
                RecodeLog.error(msg="返回:{0}".format(model_objs))
                raise APIException(
                    detail="获取到修改数据异常，请检查,数据为:{0}".format(model_objs),
                    code=API_12001_DATA_NULL_ERROR
                )
            data = self.serializer_class(
                instance=model_objs[0],
                data=request.data
            )
            if not data.is_valid():
                raise APIException(detail="修改数据格式不匹配，{}！".format(data.errors), code=API_10001_PARAMS_ERROR)
            data.save()
            return DataResponse(msg="数据保存成功：{}".format(request.data), code=API_00000_OK)
        except APIException as error:
            RecodeLog.error(msg="返回状态码:{1},错误信息:{0}".format(error.default_detail, error.status_code))
            return DataResponse(
                data=[],
                msg="数据保存失败，%s" % error.default_detail,
                code=error.status_code
            )


class BaseListView(BaseGETVIEW, BasePOSTVIEW):
    """A base view for displaying a single object."""
    serializer_class = None

    def format_request_params(self, request):
        """
        :param request:
        :return:
        """
        self.kwargs = request.GET.copy()
        if self.page_size_query_param in self.kwargs:
            self.kwargs.pop(self.page_size_query_param)
        if self.page_query_param in self.kwargs:
            self.kwargs.pop(self.page_query_param)
        if self.sort_query_param in self.kwargs:
            self.kwargs.pop(self.sort_query_param)
        if self.page_size in self.kwargs:
            self.kwargs.pop(self.page_size)

    def get(self, request):
        self.format_request_params(request=request)
        return super().get(request)

    def post(self, request):
        self.format_request_params(request=request)
        return super().post(request)


class BaseDetailView(BaseDELETEVIEW, BasePUTVIEW, BaseGETVIEW):
    serializer_class = None
    pk = None

    def format_request_params(self, request):
        """
        :param request:
        :return:
        """
        self.kwargs = request.GET.copy()
        if self.pk is None:
            raise ValueError("pk 没有定义！")
        if self.pk not in self.kwargs:
            raise APIException(
                detail="传入参数错误！",
                code=API_10001_PARAMS_ERROR
            )
        if self.page_size_query_param in self.kwargs:
            self.kwargs.pop(self.page_size_query_param)
        if self.page_query_param in self.kwargs:
            self.kwargs.pop(self.page_query_param)
        if self.sort_query_param in self.kwargs:
            self.kwargs.pop(self.sort_query_param)
        if self.page_size in self.kwargs:
            self.kwargs.pop(self.page_size)

    def get(self, request):
        self.format_request_params(request=request)
        return super().get(request)

    def put(self, request):
        self.format_request_params(request=request)
        return super().put(request)


class BaseGETView(DataQueryPermission, APIView):
    serializer_class = None
    pk = None

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
            msg="获取信息成功！",
            code='00000'
        )


class ContentFieldValueGETView(DataQueryPermission, APIView):
    serializer_class = None
    pk = None
    field = None

    def get_user_data_objects(self, request):
        self.kwargs = request.GET.copy()
        if 'field' not in self.kwargs:
            raise APIException(detail="输入参数异常!!", code=API_10001_PARAMS_ERROR)
        self.field = self.kwargs.pop('field')
        return super().get_user_data_objects(request)

    def get(self, request):
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        model_obj = self.get_user_data_objects(request=request)
        try:
            self.check_content_permission(obj=model_obj)
            data = self.get_content_field_values(field=self.field)
            return DataResponse(
                data=data,
                msg="获取信息成功！",
                code='00000'
            )
        except APIException as error:
            return DataResponse(
                data=[],
                msg="数据获取失败，%s" % error.default_detail,
                code=error.status_code
            )


class ContentFieldGETView(DataQueryPermission, APIView):
    serializer_class = None
    pk = None

    def get_user_data_objects(self, request):
        self.kwargs = getattr(request, "GET")
        return super().get_user_data_objects(request)

    def get(self, request):
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        model_obj = self.get_user_data_objects(request=request)
        try:
            self.check_content_permission(obj=model_obj)
            fields = self.get_content_fields()
            return DataResponse(
                data=fields,
                msg="获取信息成功！",
                code='00000'
            )
        except APIException as error:
            return DataResponse(
                data=[],
                msg="数据获取失败，%s" % error.default_detail,
                code=error.status_code
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
        instance = list()
        model = django_apps.get_model("Rbac.Menu")
        if self.user.is_superuser:
            RecodeLog.info(msg="当前为超级用户，用户：{0}!".format(self.user.username))
            instance = model.objects.filter(parent=None)
            data = MenuSerializer(instance=instance, many=True)
            return data.data
        else:
            for x in self.user.roles.all():
                instance = chain(x.menu.filter(parent=None), instance)
        return self.get_child_menu(childs=instance)

    # 递归获取所有的子菜单
    def get_child_menu(self, childs):
        model = django_apps.get_model("Rbac.Menu")
        children = []
        if childs:
            for child in childs:
                data = MenuSerializer(instance=child).data
                if self.user.is_superuser:
                    _childs = model.objects.filter(
                        parent=child,
                    )
                else:
                    _childs = Menu.objects.filter(
                        role__in=self.user.roles.all(),
                        parent=child
                    )
                if _childs:
                    child_data = self.get_child_menu(childs=_childs)
                    if child_data:
                        data.setdefault('children', []).extend(child_data)
                children.append(data)
        return children

    def get_roles(self):
        """
        :return:
        """
        # 判断传入参数类型
        if not isinstance(self.user, self.get_user_model):
            raise TypeError("传入的用户类型错误！")
        # 超级用户直接返回全部权限
        if self.user.is_superuser:
            RecodeLog.info(msg="当前为超级用户，用户：{0}!".format(self.user.username))
            return ['超级用户']
        else:
            return [x.name for x in self.user.roles.all()]

    def get(self, request):
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        self.user = self.get_user_object(request=request)
        data = self.serializer_class(
            instance=self.user
        )
        menu = data.data
        menu['user_permissions'] = self.get_menu()
        menu['roles'] = self.get_roles()
        RecodeLog.info(msg="返回:{0}".format(menu))
        return DataResponse(
            data=menu,
            msg="获取信息成功！",
            code='00000'
        )


class BaseGetPUTView(BaseGETVIEW, BasePUTVIEW):
    serializer_class = None
    pk = None

    def get_user_data_objects(self, request):
        self.kwargs = getattr(request, "GET")
        if self.pk is None or self.pk not in self.kwargs:
            raise APIException(
                detail="传入参数错误！",
                code=API_10001_PARAMS_ERROR
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

        try:
            if not self.check_user_permissions(request=request):
                raise APIException(detail="没有权限修改！", code=API_40003_PERMISSION_DENIED)
            model_objs = self.get_user_data_objects(request=request)
            data = self.serializer_class(
                instance=model_objs,
                many=True,
                data=request.data
            )
            if not data.is_valid():
                RecodeLog.error(msg="返回:{0}".format(data.errors))
                raise APIException(
                    detail="数据格式错误！",
                    code=API_10001_PARAMS_ERROR
                )
            data.save()
            return DataResponse(msg="数据保存成功", code="00000")
        except APIException as error:
            RecodeLog.error(msg="返回状态码:{1},错误信息:{0}".format(error.default_detail, error.status_code))
            return DataResponse(
                data=request.data,
                msg="数据保存失败:%s" % error.default_detail,
                code=error.status_code
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

        try:
            if not self.check_user_permissions(request=request):
                raise APIException(
                    code=API_40003_PERMISSION_DENIED,
                    detail="没有权限！"
                )
            model_objs = self.get_user_data_objects(request=request)
            data = self.serializer_class(
                instance=model_objs,
                many=True,
                data=request.data
            )
            if not data.is_valid():
                RecodeLog.error(msg="返回:{0}".format(data.errors))
                raise APIException(
                    detail="数据输入格式不匹配:{0}".format(data.errors),
                    code=API_10001_PARAMS_ERROR
                )
            data.save()
            return DataResponse(msg="数据保存成功：{}".format(request.data), code="00000")
        except APIException as error:
            RecodeLog.error(msg="返回状态码:{1},错误信息:{0}".format(error.default_detail, error.status_code))
            return DataResponse(
                data=request.data,
                msg="数据保存失败:%s" % error.default_detail,
                code=error.status_code
            )


__all__ = [
    'BaseDetailView',
    'BaseListView',
    'BaseGETView',
    'BaseGetPUTView',
    'BasePUTView',
    'UserGETView',
    'ContentFieldGETView',
    'ContentFieldValueGETView'
]
