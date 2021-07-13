from rest_framework.views import APIView
from lib.mixins_v2 import DataPermissionMixins
from lib.response import DataResponse
from lib.page import RewritePageNumberPagination
from Rbac.serializers import MenuSerializer, SubMenuSerializer
from Task.serializers import TemplateDBSerializers, \
    TemplateNacosSerializers, \
    TemplateKubernetesSerializers, \
    TemplateTencentServiceSerializers
from Rbac.models import Menu, UserInfo
from lib.exceptions import *
from lib.Log import RecodeLog
from django.apps import apps as django_apps
from django.db.models.query import QuerySet


class BaseGETVIEW(DataPermissionMixins, APIView, RewritePageNumberPagination):
    serializer_class = None
    pagination = True

    def init_request(self, request):
        """
        """
        self.kwargs = self.request.GET.copy()
        if self.page_size_query_param in self.kwargs:
            self.page_size = self.kwargs.pop(self.page_size_query_param)
        if self.page_query_param in self.kwargs:
            self.kwargs.pop(self.page_query_param)
        if self.sort_query_param in self.kwargs:
            self.kwargs.pop(self.sort_query_param)
        super(BaseGETVIEW, self).init_request(request=request)

    def get(self, request):
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        try:

            self.init_request(request=request)
            model_obj = self.get_model_objects()
            if self.pagination:
                page_obj = self.paginate_queryset(queryset=model_obj, request=request, view=self)
                data = self.serializer_class(
                    instance=page_obj,
                    many=True
                )
                format_data = self.data_params_quarry.format_return_data(data=data.data)
                tag = self.data_params_quarry.check_user_method_permissions(
                    method='POST'
                )
                return self.get_paginated_response(
                    data=format_data,
                    msg="获取数据成功!",
                    post=tag,
                    code=API_00000_OK
                )
            else:
                data = self.serializer_class(
                    instance=model_obj,
                    many=True
                )
                format_data = self.data_params_quarry.format_return_data(data=data.data)
                tag = self.data_params_quarry.check_user_method_permissions(
                    method='POST'
                )
                return DataResponse(
                    data=format_data,
                    msg='获取数据成功！',
                    post=tag,
                    code=API_00000_OK
                )
        except APIException as error:
            RecodeLog.error(msg="返回状态码:{1},错误信息:{0}".format(
                error.default_detail,
                error.status_code
            ))
            return DataResponse(
                code=error.status_code,
                msg=error.default_detail
            )


class BasePOSTVIEW(DataPermissionMixins, APIView):
    serializer_class = None

    def post(self, request):
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        try:
            self.init_request(request=request)
            if not self.data_params_quarry.check_user_method_permissions(
                    method=self.request.method
            ):
                raise APIException(
                    code=API_40003_PERMISSION_DENIED,
                    detail="没有权限操作"
                )
            data = self.serializer_class(
                data=self.request.data,
                user=self.user
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


class BaseResetPasswordVIEW(DataPermissionMixins, APIView):
    serializer_class = None

    def post(self, request):
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        try:
            self.init_request(request=request)
            if not self.data_params_quarry.check_user_method_permissions(
                    method=self.request.method
            ):
                raise APIException(
                    code=API_40003_PERMISSION_DENIED,
                    detail="没有权限操作"
                )
            data = self.serializer_class(
                data=self.request.data,
                user=self.user
            )
            if not data.is_valid():
                RecodeLog.error(msg="数据验证错误:{0}".format(data.errors))
                raise APIException(
                    detail="序列化数据出现异常，请检查输入参数！",
                    code=API_10001_PARAMS_ERROR,
                )
            self.user.set_password(data.data['password'])
            self.user.save()
            return DataResponse(
                data=[],
                msg='数据保存成功！',
                code=API_00000_OK
            )
        except APIException as error:
            RecodeLog.error(msg="返回状态码:{1},错误信息:{0}".format(error.default_detail, error.status_code))
            return DataResponse(
                code=error.status_code,
                msg=error.default_detail
            )


class BaseDELETEVIEW(DataPermissionMixins, APIView):
    serializer_class = None
    pk = None

    def delete(self, request):
        try:
            self.init_request(request=request)
            model_obj = self.get_model_objects()
            if not model_obj:
                raise APIException(
                    detail="获取删除数据失败！",
                    code=API_12001_DATA_NULL_ERROR
                )
            model_obj.delete()
            return DataResponse(
                code=API_00000_OK,
                msg="删除信息成功!"
            )
        except APIException as error:
            RecodeLog.error(
                msg="返回状态码:{1},错误信息:{0}".format(error.default_detail, error.status_code)
            )
            return DataResponse(
                code=error.status_code,
                msg=error.default_detail
            )


class BaseSubTaskDELETEVIEW(DataPermissionMixins, APIView):
    serializer_class = None
    pk = None

    def delete(self, request):
        try:
            self.init_request(request=request)
            model_obj = self.get_model_objects()
            if not model_obj:
                raise APIException(
                    detail="获取删除数据失败！",
                    code=API_12001_DATA_NULL_ERROR
                )
            model_obj.delete()
            model_obj.exec_list.delete()
            return DataResponse(
                code=API_00000_OK,
                msg="删除信息成功!"
            )
        except APIException as error:
            RecodeLog.error(
                msg="返回状态码:{1},错误信息:{0}".format(error.default_detail, error.status_code)
            )
            return DataResponse(
                code=error.status_code,
                msg=error.default_detail
            )


class BasePUTVIEW(DataPermissionMixins, APIView):
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
            self.init_request(request=request)
            model_objs = self.get_model_objects()
            if not model_objs or len(model_objs) > 1:
                RecodeLog.error(
                    msg="返回:{0}".format(model_objs)
                )
                raise APIException(
                    detail="获取到修改数据异常，请检查,数据为:{0}".format(model_objs),
                    code=API_12001_DATA_NULL_ERROR
                )
            data = self.serializer_class(
                instance=model_objs[0],
                data=request.data
            )
            if not data.is_valid():
                raise APIException(
                    detail="修改数据格式不匹配，{}！".format(data.errors),
                    code=API_10001_PARAMS_ERROR
                )
            data.save()
            return DataResponse(
                data=data.data,
                msg="数据保存成功！",
                code=API_00000_OK
            )
        except APIException as error:
            RecodeLog.error(
                msg="返回状态码:{1},错误信息:{0}".format(
                    error.default_detail,
                    error.status_code
                )
            )
            return DataResponse(
                data=[],
                msg="数据保存失败，%s" % error.default_detail,
                code=error.status_code
            )


class BaseListView(BaseGETVIEW, BasePOSTVIEW):
    """A base view for displaying a single object."""
    serializer_class = None


class BaseDetailView(BaseSubTaskDELETEVIEW, BasePUTVIEW, BaseGETVIEW):
    serializer_class = None
    pk = None

    def init_request(self, request):
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
        super(BaseGETVIEW, self).init_request(request=request)


class BaseGETNOTPageView(BaseGETVIEW):
    serializer_class = None
    pk = None
    pagination = False


class ContentFieldValueGETView(BaseGETVIEW):
    serializer_class = None
    pk = None
    field = None
    pagination = False

    def init_request(self, request):
        self.kwargs = self.request.GET.copy()
        if 'field' not in self.kwargs:
            raise APIException(detail="输入参数异常!!", code=API_10001_PARAMS_ERROR)
        self.field = self.kwargs.pop('field')
        return super().init_request(request=request)


class ContentTemplateValueGETView(DataPermissionMixins, APIView):
    serializer_class = None

    def get(self, request):
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        self.init_request(request=request)
        try:
            objs = self.get_model_objects().filter(
                app_label='Task',
                model__in=['templatekubernetes', 'templatenacos', 'templatetencentservice', 'templatedb']
            )
            if not objs:
                raise APIException(
                    code=API_40003_PERMISSION_DENIED,
                    detail='没有权限！'
                )
            result = []
            for obj in objs:
                template_obj = self.get_user_model_object(
                    app_label=obj.app_label,
                    model_name=obj.model,
                    kwargs=self.kwargs
                )
                if obj.model == 'templatekubernetes':
                    data = TemplateKubernetesSerializers(instance=template_obj, many=True)
                    result.append({
                        'label': 'Kubernetes模板',
                        'value': obj.id,
                        'template': data.data
                    })
                elif obj.model == 'templatenacos':
                    data = TemplateNacosSerializers(instance=template_obj, many=True)
                    result.append({
                        'label': 'Nacos模板',
                        'value': obj.id,
                        'template': data.data
                    })
                elif obj.model == 'templatetencentservice':
                    data = TemplateTencentServiceSerializers(instance=template_obj, many=True)
                    result.append({
                        'label': '腾讯云服务模板',
                        'value': obj.id,
                        'template': data.data
                    })
                elif obj.model == 'templatedb':
                    data = TemplateDBSerializers(instance=template_obj, many=True)
                    result.append({
                        'label': '数据库模板',
                        'value': obj.id,
                        'template': data.data
                    })
                else:
                    raise APIException(code=API_50001_SERVER_ERROR, detail='未处理的模板类型')
            return DataResponse(
                data=result,
                msg="获取信息成功！",
                code='00000'
            )
        except APIException as error:
            return DataResponse(
                data=[],
                msg="获取信息失败,{}".format(error.default_detail),
                code='00001'
            )


class ContentFieldGETView(DataPermissionMixins, APIView):
    serializer_class = None
    pk = None

    def init_request(self, request):
        """
        """
        self.kwargs = self.request.GET.copy()
        super(ContentFieldGETView, self).init_request(request=request)

    def get(self, request):
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        fields_list = list()
        self.init_request(request=request)
        model_obj = self.get_model_objects()
        try:
            self.data_params_quarry.check_content_permission(obj=model_obj)
            fields = self.data_params_quarry.get_content_fields()
            for key, value in fields.items():
                field_value = self.data_params_quarry.get_content_field_values(field=key)
                fields_list.append({
                    'field': key,
                    'value': field_value
                })
            return DataResponse(
                data=fields_list,
                msg="获取信息成功！",
                code='00000'
            )
        except APIException as error:
            return DataResponse(
                data=[],
                msg="数据获取失败，%s" % error.default_detail,
                code=error.status_code
            )


class UserGETView(DataPermissionMixins, APIView):
    serializer_class = None
    pk = None

    def get_menu(self):
        """
        :return:
        """
        # 超级用户直接返回全部权限
        model = django_apps.get_model("Rbac.Menu")
        if self.user.is_superuser:
            RecodeLog.info(msg="当前为超级用户，用户：{0}!".format(self.user.username))
            instance = model.objects.filter(parent=None)
            data = MenuSerializer(instance=instance, many=True)
            return data.data
        else:
            data = self.get_user_menu(menu_list=self.user.roles.menu.all())
        return data

    @staticmethod
    def get_user_menu(menu_list):
        """

        :param menu_list:
        :return:
        """
        menu_dict = dict()
        menu = list()
        if not isinstance(menu_list, QuerySet):
            raise APIException(
                code=API_50001_SERVER_ERROR,
                detail="输入类型错误！"
            )
        for x in menu_list:
            if not isinstance(x, Menu):
                raise APIException(
                    code=API_50001_SERVER_ERROR,
                    detail="菜单类型解构错误！"
                )
            menu_data = SubMenuSerializer(instance=x).data

            if x.parent:
                try:
                    data = SubMenuSerializer(instance=x)
                except Exception as error:
                    raise APIException(
                        detail=error,
                        code=API_50001_SERVER_ERROR
                    )
                menu_dict.setdefault(
                    "{}".format(x.parent.pk),
                    []
                ).append(data.data)
            elif not x.parent:
                menu.append(menu_data)
        menu_pk_list = [x['id'] for x in menu]
        for key, value in menu_dict.items():
            obj = Menu.objects.get(id=key)
            try:
                data = SubMenuSerializer(instance=obj)
            except Exception as error:
                raise APIException(
                    detail=error,
                    code=API_50001_SERVER_ERROR
                )
            tmp = data.data
            tmp['children'] = value
            if tmp['id'] in menu_pk_list:
                menu = [tmp if x['id'] == tmp['id'] else x for x in menu]
            else:
                menu.append(tmp)

        return menu

    def get_roles(self):
        """
        :return:
        """
        # 超级用户直接返回全部权限
        if self.user.is_superuser:
            RecodeLog.info(msg="当前为超级用户，用户：{0}!".format(self.user.username))
            return ['超级用户']
        else:
            return [self.user.roles.name]

    def get(self, request):
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        self.init_request(request=request)
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

    def init_request(self, request):
        self.kwargs = getattr(self.request, "GET")
        if self.pk is None or self.pk not in self.kwargs:
            raise APIException(
                detail="传入参数错误！",
                code=API_10001_PARAMS_ERROR
            )
        self.pagination = False
        return super().init_request(request=request)


class BaseFlowGETVIEW(DataPermissionMixins, APIView, RewritePageNumberPagination):
    serializer_class = None

    def get(self, request):
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        try:
            self.init_request(request=request)
            model_obj = self.get_model_objects()
            page_obj = self.paginate_queryset(
                queryset=model_obj,
                request=request,
                view=self
            )
            data = self.serializer_class(
                instance=page_obj,
                many=True
            )

            format_data = self.data_params_quarry.format_flow_data(
                data=data.data
            )
            tag = self.data_params_quarry.check_user_method_permissions(
                method=self.request.method
            )
            return self.get_paginated_response(
                data=format_data,
                msg="获取数据成功",
                post=tag,
                code=API_00000_OK
            )
        except APIException as error:
            RecodeLog.error(msg="返回状态码:{1},错误信息:{0}".format(
                error.default_detail,
                error.status_code
            ))
            return DataResponse(
                code=error.status_code,
                msg=error.default_detail
            )


class BaseFlowPUTVIEW(DataPermissionMixins, APIView, RewritePageNumberPagination):
    serializer_class = None
    pk = None
    fields = None

    def init_request(self, request):
        """
        """
        self.kwargs = self.request.GET.copy()
        if self.pk is None or self.pk not in self.kwargs:
            raise APIException(
                detail="传入参数错误！",
                code=API_10001_PARAMS_ERROR
            )
        if self.page_size_query_param in self.kwargs:
            self.page_size = self.kwargs.pop(self.page_size_query_param)
        if self.page_query_param in self.kwargs:
            self.kwargs.pop(self.page_query_param)
        if self.sort_query_param in self.kwargs:
            self.kwargs.pop(self.sort_query_param)
        super(BaseFlowPUTVIEW, self).init_request(request=request)

    def put(self, request):
        """
        :param request:
        :return:
        """
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        try:
            self.init_request(request=request)
            model_objs = self.get_model_objects()
            if not model_objs or len(model_objs) > 1:
                RecodeLog.error(
                    msg="返回:{0}".format(model_objs)
                )
                raise APIException(
                    detail="获取到修改数据异常，请检查,数据为:{0}".format(model_objs),
                    code=API_12001_DATA_NULL_ERROR
                )
            data = self.serializer_class(
                instance=model_objs[0],
                data=request.data,
                fields=self.fields
            )
            if not data.is_valid():
                raise APIException(
                    detail="修改数据格式不匹配，{}！".format(data.errors),
                    code=API_10001_PARAMS_ERROR
                )
            data.save()
            return DataResponse(
                msg="数据保存成功!",
                data=request.data,
                code=API_00000_OK
            )
        except APIException as error:
            RecodeLog.error(
                msg="返回状态码:{1},错误信息:{0}".format(
                    error.default_detail,
                    error.status_code
                )
            )
            return DataResponse(
                data=[],
                msg="数据保存失败，%s" % error.default_detail,
                code=error.status_code
            )


__all__ = [
    'BaseDetailView',
    'BaseListView',
    'BasePOSTVIEW',
    'BaseGETNOTPageView',
    'BaseGetPUTView',
    'UserGETView',
    'BaseFlowGETVIEW',
    'BaseFlowPUTVIEW',
    'ContentFieldGETView',
    'ContentFieldValueGETView',
    'BaseResetPasswordVIEW',
    'ContentTemplateValueGETView'
]
