from django.apps import apps as django_apps
from KubernetesManagerWeb.settings import AUTH_USER_MODEL
from Rbac.serializers import MenuSerializer
from rest_framework.pagination import PageNumberPagination
import time
import datetime
import hashlib
from KubernetesManagerWeb.settings import SECRET_KEY


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
            return user.objects.get(usertoken__token=token)
        except user.DoesNotExist:
            return None


class UserPagination(PageNumberPagination):
    page_size = 6
    page_query_param = 'page'
    page_size_query_param = 'size'


def make_token(username):
    """
    :param username:
    :return:
    """
    md5 = hashlib.md5(
        "{0}{1}{2}".format(username, time.time(), SECRET_KEY).encode("utf8")
    )
    return md5.hexdigest()


class DataQueryPermission(ObjectUserInfo):
    def __init__(self, request):
        ObjectUserInfo.__init__(self)
        self.user = self.get_user_object(request=request)
        self.__object = None
        self.__model = None

    def get_user_data_permission(self):
        """
        :return:
        """
        model = django_apps.get_model("Rbac.DataPermissionList")
        if not self.user.usertoken.expiration_time > datetime.datetime.now() or not self.user.is_active:
            return []
        return [data for data in model.objects.filter(
            role__in=self.user.roles.all()
        )]

    def get_user_model_data_permission(self, app_label, model_name):
        """
        :param app_label:
        :param model_name:
        :return:
        """
        if not isinstance(model_name, str):
            return []
        params = dict()
        self.__model = django_apps.get_model("{0}.{1}".format(app_label, model_name))
        # 超级管理员直接返回结果
        if self.user.is_superuser and self.user.is_active:
            self.__object = self.__model.model_class().objects.all()
            return self.__object
        # 用户状态为不生效，返回空
        elif not self.user.is_active:
            return self.__object
        for data in self.get_user_data_permission():
            if data.content_type != self.__model:
                continue
            try:
                value = int(data.value)
            except TypeError:
                value = data.value
            params.setdefault(data.check_field, []).append(value)
        filter_dict = dict()
        for key, value in params.items():
            if len(value) == 0:
                continue
            elif len(value) == 1:
                filter_dict = {key: value}
            else:
                filter_dict = {"{0}__in".format(key): value}
        self.__object = self.__model.model_class().objects.filter(**filter_dict)
        return self.__object

    def get_model_fields(self):
        if not self.__object:
            return []
        if not self.__model:
            raise ValueError("请先通过 get_user_model_data_permission实例化相关数据！")
        return [x.name for x in self.__model._meta.fields]

    def get_field_values(self, field):
        """
        :param field:
        :return:
        """
        if not self.__object:
            raise ValueError("请先通过 get_user_model_data_permission实例化相关数据！")
        fields = self.get_model_fields()
        if field not in fields:
            return []
        return list(set([getattr(x, field) for x in self.__object]))

    def check_user_permission(self, model_obj):
        """
        :param model_obj:
        :return:
        """
        check_status = False
        data_permission = self.get_user_data_permission()
        for data in data_permission:
            if model_obj != data:
                continue
            else:
                check_status = True
                break
        return check_status


class UserResourceQuery(DataQueryPermission):
    def __init__(self, request):
        DataQueryPermission.__init__(self, request=request)

    def get_menu(self):
        """
        :return:
        """
        # 判断传入参数类型
        if not isinstance(self.user, self.get_user_model):
            raise TypeError("传入的用户类型错误！")
        # 超级用户直接返回全部权限
        instance = self.get_user_model_data_permission(app_label='Rbac', model_name='Menu')
        data = MenuSerializer(many=True, instance=instance)
        return data.data
