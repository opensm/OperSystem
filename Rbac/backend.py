from django.apps import apps as django_apps
from KubernetesManagerWeb.settings import AUTH_USER_MODEL
from Rbac.serializers import PermissionSerializer
from Rbac.models import Permission, UserInfo


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
        return self.get_child_menu(childs=instance, user=user_obj)

    # 递归获取所有的子菜单
    def get_child_menu(self, childs, user):
        children = []
        if not childs:
            return []
        for child in childs:

            params = {
                'parent': child
            }
            if not user.is_superuser:
                params['role__userinfo'] = user

            data = PermissionSerializer(instance=child).data

            _childs = Permission.objects.filter(**params)
            if not _childs:
                continue

            child_data = self.get_child_menu(childs=_childs, user=user)
            if child_data:
                data.setdefault('children', []).extend(child_data)
            children.append(data)

        return children
