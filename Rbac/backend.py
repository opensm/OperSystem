from django.apps import apps as django_apps
from KubernetesManagerWeb.settings import AUTH_USER_MODEL
from Rbac.serializers import PermissionSerializer
from Rbac.models import Permission, UserInfo, DataPermissionList
from django.contrib.contenttypes.models import ContentType
from rest_framework.pagination import PageNumberPagination
import time, datetime
import hashlib
from KubernetesManagerWeb.settings import SECRET_KEY


class ObjectUserInfo:
    def __init__(self):
        self.user_object_type = django_apps.get_model(AUTH_USER_MODEL)
        self.token = None
        self.button_code = 999

    @staticmethod
    def get_user_model():
        return django_apps.get_model(AUTH_USER_MODEL)

    def get_user_object(self, token):
        user = self.get_user_model()
        try:
            return user.objects.get(usertoken__token=token)
        except user.DoesNotExist:
            return None

    def get_menu(self, user_obj):
        """
        :param user_obj:
        :return:
        """
        # 判断传入参数类型
        if not isinstance(user_obj, self.get_user_model()):
            raise TypeError("传入的用户类型错误！")
        # 超级用户直接返回全部权限
        if user_obj.is_superuser:
            instance = Permission.objects.filter(
                parent=None
            ).exclude(level=self.button_code)
        else:
            instance = Permission.objects.filter(
                role__userinfo=user_obj,
                parent=None
            ).exclude(level=self.button_code)
        data = PermissionSerializer(many=True, instance=instance)
        return data.data


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


class BackendPermission:
    def __init__(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        self.user = UserInfo.objects.get(usertoken__token=token)

    def get_user_data_permission(self):
        """
        :return:
        """
        if not self.user.usertoken.expiration_time > datetime.datetime.now() or not self.user.is_active:
            return []
        return [data.content_object for data in DataPermissionList.objects.filter(
            role__in=self.user.roles.objects.all()
        )]

    def get_user_model_data_permission(self, model_name):
        """
        :param model_name:
        :return:
        """
        for data in self.get_user_data_permission():
            print(data)

    # user = ContentType.objects.get(app_label=app_label, model=user_obj).model_class()
    # user.objects.get()

    def check_user_permission(self, model_obj):
        """
        :param model_obj:
        :return:
        """
        check_status = False
        data_permission = self.get_user_data_permission()
        for data in data_permission:
            print(data.content_type)
            if model_obj != data:
                continue
            else:
                check_status = True
                break
        return check_status

    # @staticmethod
    # def get_user_model_obj(models, *args, **kwargs):
    #     """
    #     :param models:
    #     :param args:
    #     :param kwargs:
    #     :return:
    #     """
    #     if not isinstance(models, list):
    #         raise TypeError("models type error!")


