from django.apps import apps as django_apps
from django.db.models import Q
from KubernetesManagerWeb.settings import AUTH_USER_MODEL
import datetime
import hashlib
import time
import operator
from functools import reduce
from KubernetesManagerWeb.settings import SECRET_KEY
from lib.exceptions import *
from Rbac.models import UserInfo, DataPermissionRule, DataPermissionList
# from Flow.models import FlowTask
from Task.models import Tasks,FlowTask
from django.contrib.contenttypes.models import ContentType
from lib.Log import RecodeLog


def make_token(username):
    """
    :param username:
    :return:
    """
    md5 = hashlib.md5(
        "{0}{1}{2}".format(username, time.time(), SECRET_KEY).encode("utf8")
    )
    return md5.hexdigest()


class ObjectUserInfo:
    def __init__(self, request):
        self.user_object_type = django_apps.get_model(AUTH_USER_MODEL)
        self.token = None
        self.request = request

    @property
    def get_user_model(self):
        return django_apps.get_model(AUTH_USER_MODEL)

    def get_user_object(self):

        try:
            token = self.request.META.get('HTTP_AUTHORIZATION')
            user = self.get_user_model
            return user.objects.get(usertoken__token=token)
        except UserInfo.DoesNotExist:
            raise APIException(
                code=API_40001_AUTH_ERROR,
                detail="用户登录失效"
            )


class DataQueryPermission(ObjectUserInfo):
    kwargs = None

    def __init__(self, request, app_label, model_name, kwargs):
        ObjectUserInfo.__init__(self, request=request)
        self.user = self.get_user_object()
        self.kwargs = kwargs
        self.__object = None
        self.__model_class = None
        self.__data_permission = django_apps.get_model("Rbac.DataPermissionList")
        try:
            self.__model = django_apps.get_model(
                "{0}.{1}".format(
                    app_label, model_name
                )
            )
            self.__content_type = ContentType.objects.get(
                app_label=app_label,
                model=model_name
            )
        except ContentType.DoesNotExist:
            raise APIException(
                code=API_50001_SERVER_ERROR,
                detail="获取模型数据异常！"
            )
        if not self.user.usertoken.expiration_time > datetime.datetime.now() or not self.user.is_active:
            raise APIException(
                code=API_40003_PERMISSION_DENIED,
                detail="认证超时或者用户未激活！"
            )

    def get_data_permission_params(self):
        """
        获取所有用户的数据权限
        :return:
        """
        if not isinstance(self.user, self.get_user_model):
            raise TypeError("用户表类型错误！")
        permission_list = list()
        for content in self.user.roles.data_permission.filter(
                content_type=self.__content_type,
                request_type__method=self.request.method
        ):
            try:
                permission = DataPermissionList.objects.filter(
                    permission_rule=content
                )
            except self.__data_permission.DoesNotExist:
                continue
            if not permission and not content.is_all:
                continue
            permission_list.append((
                permission,
                content.request_type,
                content.is_all
            ))
        return permission_list

    def check_user_method_permissions(self, method):
        """
        :param method:
        :return:
        """
        if self.user.is_superuser and self.user.is_active:
            return True
        data = self.get_data_permission_params()
        status = False
        for content in data:
            if method in [x.method for x in content[1].all()]:
                status = True
        return status

    def get_permission_rule_q_sum(self):
        """
        :return:
        """
        q_query = list()
        permission_data = self.get_data_permission_params()
        for data in permission_data:
            if data[2]:
                q_query.append('all')
            else:
                obj, methods = self.get_permission_rule_q(data=data)
                q_query.append(obj)
        return q_query

    def check_permission(self, method, data):
        """
        :param method:
        :param data:
        :return:
        """
        if not isinstance(data, tuple):
            raise APIException(
                code=API_50001_SERVER_ERROR,
                detail="类型错误!!!"
            )

        # 判断是否为全部权限
        if data[2]:
            return data[2]
        else:
            current_obj = self.get_request_filter()
            obj, methods = self.get_permission_rule_q(data=data)
            RecodeLog.info(msg="获取数据:{},{}".format(obj, methods))
            if len(obj) > 1:
                obj_filter = reduce(operator.or_, obj)
            else:
                obj_filter = obj

            # 判断GET请求的时候数据为空和没有数据权限的两种情况
            if method == 'GET' and not self.kwargs:
                RecodeLog.info(msg="传入参数:{}".format(self.kwargs))
                if not self.__model.objects.all():
                    if obj_filter:
                        return method in [x.method for x in methods.all()]
                    else:
                        return False

            if not current_obj:
                return method in [x.method for x in methods.all()] and self.__model.objects.filter(obj_filter)
            else:
                return method in [x.method for x in methods.all()] and current_obj.filter(obj_filter)

    def check_user_permissions(self, request):
        """
        :param request:
        :return:
        """
        if self.user.is_superuser and self.user.is_active:
            return True
        for data in self.get_data_permission_params():
            RecodeLog.info(msg="获取权限表数据:{}".format(data))
            if self.check_permission(method=request.method, data=data):
                return True
        return False

    def request_method(self, params):
        """
        :return:
        """
        # 用户状态为不生效，返回空
        if not self.user.is_active:
            raise APIException(
                detail="用户未激活！",
                code=API_40003_PERMISSION_DENIED
            )
        if self.user.is_superuser:
            method_type = django_apps.get_model("Rbac.RequestType").objects.values('method')
            if not method_type:
                raise APIException(
                    code=API_50001_SERVER_ERROR,
                    detail='请初始化method表！'
                )
            return [x['method'] for x in method_type]
        for data in self.get_data_permission_params():
            if data[2]:
                return [x.method for x in data[1].all()]
            else:
                obj, methods = self.get_permission_rule_q(data=data)
                if not obj:
                    continue
                if len(obj) > 1:
                    obj_filter = reduce(operator.or_, obj)
                else:
                    obj_filter = obj
                if not self.__model.objects.filter(
                        obj_filter & Q(id=params['id'])
                ):
                    continue
                else:
                    return [x.method for x in methods.all()]

    def format_return_data(self, data):
        """
        :param data:
        :return:
        """
        data_list = list()
        if not isinstance(data, list):
            raise APIException(
                detail="输入的数据类型错误，请输入list类型!",
                code=API_50001_SERVER_ERROR
            )
        for x in data:
            methods = self.request_method(params=x)
            x['button'] = methods
            data_list.append(
                x
            )
        return data_list

    def format_flow_data(self, data):
        """
        :param data:
        :return:
        """
        data_list = list()
        status_for_approved = ['fail_approve', 'ok_approved', 'progressing', 'success', 'fail', 'timeout']
        if not isinstance(data, list):
            raise APIException(
                detail="输入的数据类型错误，请输入list类型!",
                code=API_50001_SERVER_ERROR
            )
        for x in data:
            methods = self.request_method(params=x)
            for y in FlowTask.objects.filter(
                    id=x['id']
            ).values('task', 'flow', 'level'):
                level = y.pop('level')
                flow_data = FlowTask.objects.filter(
                    **y,
                    level__lt=level,
                    status__in=['unprocessed', 'refuse']
                )
                flowing_data = FlowTask.objects.filter(
                    **y,
                    level__gt=level,
                    status__in=['pass', 'refuse']
                )
                if Tasks.objects.get(id=y['task']).status in status_for_approved:
                    x['button'] = []
                else:
                    if not flow_data and 'PUT' in methods and not flowing_data:
                        x['button'] = 'PUT'
                    else:
                        x['button'] = []
            data_list.append(
                x
            )
        return data_list

    @staticmethod
    def format_query_set(query_set):
        """
        :return:
        :param query_set:
        :return:
        """
        params = dict()
        for y in query_set:
            if not isinstance(y, DataPermissionList):
                raise TypeError('检验模型类型错误！')
            split_value = y.value.split(',')
            for x in split_value:
                try:
                    value = int(x)
                except ValueError:
                    value = x
                params.setdefault(y.check_field, []).append(value)
        return params

    def get_permission_rule_q(self, data):
        """
        :param data:
        :return:
        """
        predicates = list()
        if not isinstance(data, tuple):
            raise TypeError("输入参数必须为元组:{0}，请检查".format(data))
        query_set = data[0]
        method = data[1]
        if not method:
            raise ValueError("没有相关的请求类型")
        params = self.format_query_set(query_set=query_set)
        if len(params.keys()) > 1:
            for key, value in params.items():
                predicates.append(
                    Q(**{"{}__in".format(key): value})
                )
            return (
                predicates, method
            )
        elif len(params.keys()) == 1:
            for key, value in params.items():
                if len(value) > 0:
                    return (
                        Q(**{"{}__in".format(key): value}), method
                    )
                else:
                    raise APIException(
                        detail="权限表配置异常",
                        code=API_50001_SERVER_ERROR
                    )
        else:
            return (
                None, None
            )

    def get_model_fields(self):
        field_name = dict()
        if not self.__model:
            raise ValueError("请先输入model参数实例化相关数据！")
        for x in self.__model._meta.fields:
            field_name[x.name] = x.verbose_name
        return field_name

    def get_field_values(self, field):
        """
        :param field:
        :return:
        """
        if not self.__object:
            raise ValueError("请先实例化相关数据！")
        fields = self.get_model_fields()
        if field not in fields.keys():
            return []
        return list(set([getattr(x, field) for x in self.__object]))

    def get_content_fields(self):
        """
        :return:
        """
        field_name = dict()
        if not self.__model_class:
            raise ValueError("请先输入model参数实例化相关数据！")
        for x in self.__model_class._meta.fields:
            field_name[x.name] = x.verbose_name
        return field_name

    def get_content_field_values(self, field):
        """
        :param field:
        :return:
        """
        if not self.__model_class:
            raise ValueError("请先实例化相关数据！")
        # if len(field) > 1:
        #     raise ValueError("请输入一个字段！")
        fields = self.get_content_fields()
        if field not in list(fields.keys()):
            return []
        data = list()
        for x in self.__model_class.objects.values('{0}'.format(field)).distinct():
            data.append(str(x[field]))
        return data

    def check_user_permission(self, model_obj, request_type='POST'):
        """
        :param model_obj:
        :param request_type:
        :return:
        """
        for data in self.get_data_permission_params():
            if model_obj in data[0] and request_type in data[1]:
                return True
        return False

    def get_request_filter(self):
        """
        :return:
        """
        fields = self.get_model_fields()
        if len(self.kwargs.keys()) == 0:
            return
        else:
            query_params = dict()
            for key in self.kwargs.keys():
                if key not in fields or not self.kwargs.getlist(key):
                    raise APIException(
                        detail='输入参数错误:{}'.format(key),
                        code=API_10001_PARAMS_ERROR
                    )
                query_params["{}__in".format(key)] = self.kwargs.getlist(key)
            return Q(**query_params)

    def get_user_data_objects(self):
        """
        :return:
        """
        current_obj = self.get_request_filter()
        # 超级管理员直接返回结果
        if self.user.is_superuser:
            if not current_obj:
                return self.__model.objects.all()
            else:
                return self.__model.objects.filter(current_obj)
        else:
            permissions = self.get_permission_rule_q_sum()
            if not permissions:
                raise APIException(
                    code=API_40003_PERMISSION_DENIED,
                    detail="没有相关权限！"
                )
            # all permission
            if 'all' in permissions:
                if current_obj:
                    operator_params = current_obj
                else:
                    operator_params = 'all'
            else:
                if current_obj:
                    if len(permissions) > 1:
                        operator_params = reduce(
                            operator.and_, [
                                current_obj,
                                reduce(operator.or_, permissions)
                            ])
                    else:
                        operator_params = reduce(
                            operator.and_,
                            [current_obj, permissions]
                        )
                    select_obj = self.__model.objects.filter(current_obj)
                    request_obj = self.__model.objects.filter(operator_params)
                    if select_obj and not request_obj:
                        raise APIException(
                            code=API_40003_PERMISSION_DENIED,
                            detail="没有权限！"
                        )
                else:
                    operator_params = reduce(
                        operator.or_,
                        permissions
                    )
            if operator_params == 'all':
                return self.__model.objects.all()
            else:
                return self.__model.objects.filter(operator_params)

    def check_content_permission(self, obj):
        """
        :return:
        """
        model = None
        if len(obj) == 0:
            raise APIException(
                detail="输入数据类型错误！",
                code=API_50001_SERVER_ERROR
            )

        for data in obj:
            if not isinstance(data, DataPermissionRule):
                raise APIException(
                    detail="模型类型错误！",
                    code=API_50001_SERVER_ERROR
                )
            else:
                model = data.content_type
                if 'GET' not in [x.method for x in data.request_type.all()]:
                    raise APIException(
                        detail='没有权限！',
                        code=API_50001_SERVER_ERROR
                    )
        self.__model_class = model.model_class()


class DataPermissionMixins:
    model_name = None
    app_label = None
    kwargs = None

    def __init__(self):
        self.request = None
        self.data_params_quarry = None
        self.user = None

    def init_request(self, request):
        self.request = request
        self.data_params_quarry = DataQueryPermission(
            request=request,
            app_label=self.app_label,
            model_name=self.model_name,
            kwargs=self.kwargs
        )
        self.user = self.data_params_quarry.user

    def get_model_objects(self):
        if not isinstance(self.data_params_quarry, DataQueryPermission):
            raise APIException(
                code=API_50001_SERVER_ERROR,
                detail="初始化参数失败！"
            )
        return self.data_params_quarry.get_user_data_objects()
