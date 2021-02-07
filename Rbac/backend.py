from django.apps import apps as django_apps
from KubernetesManagerWeb.settings import AUTH_USER_MODEL
from Rbac.serializers import PermissionSerializer
from Rbac.models import Permission, UserInfo, DataPermissionList
from django.contrib.contenttypes.models import ContentType
from rest_framework.pagination import PageNumberPagination
import time
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
    def __init__(self):
        pass

    def get_user_permission(self, request):
        """
        :param request:
        :return:
        """
        token = request.META.get('HTTP_AUTHORIZATION')
        user = UserInfo.objects.get(usertoken__token=token)
        return [data.content_object for data in DataPermissionList.objects.filter(
            role__in=user.roles.objects.all()
        )]

    # user = ContentType.objects.get(app_label=app_label, model=user_obj).model_class()
    # user.objects.get()

    def check_user_permission(self, request, model_obj):
        """
        :param request:
        :param model_obj:
        :return:
        """
        check_status = False
        data_permission = self.get_user_permission(request=request)
        for data in data_permission:
            if model_obj != data:
                continue
            else:
                check_status = True
                break
        return check_status
