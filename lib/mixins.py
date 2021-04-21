from django.apps import apps as django_apps
from django.db.models import query
from django.db.models import Q
from KubernetesManagerWeb.settings import AUTH_USER_MODEL
import datetime
import hashlib
import time
from KubernetesManagerWeb.settings import SECRET_KEY
from lib.exceptions import *
from Rbac.models import UserInfo, UserToken
from django.contrib.contenttypes.models import ContentType


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
    def __init__(self):
        self.user_object_type = django_apps.get_model(AUTH_USER_MODEL)
        self.token = None
        self.button_code = 999

    @property
    def get_user_model(self):
        return django_apps.get_model(AUTH_USER_MODEL)

    def get_user_object(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        user = self.get_user_model
        try:
            # return UserInfo.objects.get(usertoken__token=token)
            return user.objects.get(usertoken__token=token)
        except UserInfo.DoesNotExist:
            raise APIException(code=API_40001_AUTH_ERROR, detail="用户登录失效")


class DataQueryPermission(ObjectUserInfo):
    model_name = None
    app_label = None
    error_message = []
    kwargs = None

    def __init__(self):
        ObjectUserInfo.__init__(self)
        self.user = None
        self.__object = None
        self.__model = django_apps.get_model(
            "{0}.{1}".format(
                self.app_label, self.model_name
            )
        )

    def get_user_data_permission(self):
        """
        :return:
        """
        if not isinstance(self.user, self.get_user_model):
            raise TypeError("用户表类型错误！")
        model = django_apps.get_model("Rbac.DataPermissionList")
        if not self.user.usertoken.expiration_time > datetime.datetime.now() or not self.user.is_active:
            return []
        permission_list = list()
        for role in self.user.roles.all():
            # for content in role.data_permission.all():
            for content in role.data_permission.filter(
                    content_type=ContentType.objects.get(app_label=self.app_label, model=self.model_name)
            ):
                try:
                    permission = model.objects.filter(
                        permission_rule=content,
                    )
                except model.DoesNotExist:
                    continue
                if not permission:
                    continue
                permission_list.append((
                    permission,
                    content.request_type
                ))
        return permission_list

    def get_user_method_permission(self):
        """
        :return:
        """
        if not isinstance(self.user, self.get_user_model):
            raise TypeError("用户表类型错误！")
        if not self.user.usertoken.expiration_time > datetime.datetime.now() or not self.user.is_active:
            return []
        permission_list = list()
        for role in self.user.roles.all():
            # for content in role.data_permission.all():
            for content in role.data_permission.filter(
                    content_type=ContentType.objects.get(app_label=self.app_label, model=self.model_name)
            ):
                permission_list.append(
                    content
                )
        return permission_list

    def check_user_method_permissions(self, request):
        """
        :param request:
        :return:
        """
        self.user = self.get_user_object(request=request)
        data = self.get_user_method_permission()
        print("************{0}*************".format(data))
        status = False
        for content in data:
            print("9999999999{0}9999999999999".format(content))
            request_data = [x.method for x in content.request_type.all()]
            print(request_data)
            if request.method in request_data:
                status = True
        return status

    def get_user_model_data_permission(self):
        """
        :return:
        """
        q_query = list()

        if not isinstance(self.model_name, str):
            return []
        if not self.__model:
            raise ValueError("french model value error!")

        # 用户状态为不生效，返回空
        elif not self.user.is_active:
            return []
        for data in self.get_user_data_permission():
            obj, methods = self.get_permission_rule_q(data=data)
            q_query.append(obj)
            print(q_query)
        return q_query

    def check_user_permissions(self, request):
        """
        :param request:
        :return:
        """
        self.user = self.get_user_object(request=request)
        current_obj = self.get_request_filter(request=request)
        if self.user.is_superuser and self.user.is_active:
            return True
        status = False
        for data in self.get_user_data_permission():
            # q = Q()
            obj, methods = self.get_permission_rule_q(data=data)
            # q.add(obj, 'ADD')
            print("++++++++++++++++++++++++++++++++++++++")
            print(obj)
            print("++++++++++++++++++++++++++++++++++++++")
            if not current_obj:
                if request.method in methods and self.__model.objects.filter(obj):
                    status = True
                    break
            else:
                if request.method in methods and current_obj.filter(obj):
                    status = True
                    break
        return status

    def get_permission_rule_q(self, data):
        """
        :param data:
        :return:
        """
        params = dict()
        if not isinstance(data, tuple):
            raise TypeError("输入参数必须为元组:{0}，请检查".format(data))
        query_set = data[0]
        method = data[1]
        if not method:
            raise ValueError("没有相关的请求类型")
        print("*****************************************************")
        print(query_set)
        print(method)
        print("*****************************************************")
        if not query_set:
            return []
        for x in query_set:
            params.setdefault(
                x.check_field,
                []
            ).append(x.value)
        a = Q()
        if len(params.keys()) > 1:
            print("2++++++++++++++++++++++++++++")
            for key, value in params.items():
                a_t = Q()
                a_t.connector = 'OR'
                for v in value:
                    a_t.children.append((key, v))
                a.add(a_t, 'ADD')
            return (
                a, method
            )
        else:
            print("1++++++++++++++++++++++++++++")
            for key, value in params.items():
                # a.add(data={key, value}, conn_type=a.OR)
                # for v in value:
                #     a.add(Q(**{key: v}), Q.OR)
                a_t = Q()
                a_t.connector = 'OR'
                for v in value:
                    a_t.children.append((key, v))
                a.add(a_t, 'ADD')
            print((
                a, method
            ))
            return (
                a, method
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
            raise ValueError("请先通过 get_user_model_data_permission实例化相关数据！")
        fields = self.get_model_fields()
        if field not in fields.keys():
            return []
        return list(set([getattr(x, field) for x in self.__object]))

    def check_user_permission(self, model_obj, request_type='POST'):
        """
        :param model_obj:
        :param request_type:
        :return:
        """
        for data in self.get_user_data_permission():
            if model_obj in data[0] and request_type in data[1]:
                return True
        return False

    def get_request_filter(self, request):
        """
        :param request:
        :return:
        """
        kwargs = getattr(request, "GET")
        fields = self.get_model_fields()
        if len(kwargs.keys()) == 0:
            return
        else:
            query_params = dict()
            for key in kwargs.keys():
                if key not in fields or not kwargs.getlist(key):
                    raise APIException(detail='输入参数错误', code=API_10001_PARAMS_ERROR)
                query_params["{}__in".format(key)] = kwargs.getlist(key)
            return self.__model.objects.filter(**query_params)

    def get_user_data_objects(self, request):
        """
        :return:
        """
        self.user = self.get_user_object(request=request)
        current_obj = self.get_request_filter(request=request)
        # 超级管理员直接返回结果
        if self.user.is_superuser and self.user.is_active:
            if not current_obj:
                return self.__model.objects.all()
            else:
                return current_obj.all()
        elif not self.user.is_superuser and self.user.is_active:
            permissions = self.get_user_model_data_permission()
            if not permissions:
                return []
            permissions = self.get_user_model_data_permission()
            parent_q = Q()
            for data in permissions:
                sub_q = Q()
                sub_q.connector = 'AND'
                sub_q.children.append(data)
                parent_q.add(sub_q, 'OR')
            if current_obj:
                return current_obj.filter(parent_q)
            else:
                return self.__model.objects.filter(parent_q)
        else:
            raise APIException(
                code=API_40003_PERMISSION_DENIED,
                detail="没有操作权限！"
            )
