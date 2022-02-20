from Rbac.models import UserInfo, Role


def get_identity(identity):
    """
    :param identity:
    :return:
    """
    if isinstance(identity, list) and (identity[0] == UserInfo):
        return identity, None
    elif isinstance(identity, list) and (identity[0] == Role):
        return None, identity
    if isinstance(identity, UserInfo):
        return identity, None
    if isinstance(identity, Role):
        return None, identity

    raise ValueError("错误的类型请检查！")


def get_user_model():
    """
    :return:
    """


class ObjectPermissionChecker:

    def __init__(self, user_or_roles):
        """
        :param user_or_roles:
        """
        self.user, self.group = get_identity(user_or_roles)

    def has_perm(self, perm, obj):
        """
        :param perm:
        :param obj:
        :return:
        """
        if self.user and not self.user.is_active:
            return False
        elif self.user and self.user.is_superuser:
            return True

        if '.' in perm:
            _, perm = perm.split('.', 1)
        return perm in self.get_perms(obj)

    def get_perms(self, obj):
        pass
