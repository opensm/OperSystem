import datetime
from django.contrib import auth
from django.contrib.auth import password_validation
from django.contrib.contenttypes.models import ContentType
from Rbac.models import Role, UserInfo, DataPermissionRule, Menu, RequestType
from rest_framework import serializers


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class RequestTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestType
        fields = ("__all__")


class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ("__all__")


class DataPermissionSerializer(serializers.ModelSerializer):
    request_type = RequestTypeSerializer(
        many=True, read_only=True,
    )
    content_type = ContentTypeSerializer(
        read_only=True,
    )

    class Meta:
        model = DataPermissionRule
        fields = ("__all__")


class ParentMenuSerializer(serializers.ModelSerializer):
    class Meta:  # 如果不想每个字段都自己写，那么这就是固定写法，在继承serializer中字段必须自己写，这是二者的区别
        model = Menu  # 指定需要序列化的模型表
        fields = ("__all__")


class MenuSerializer(serializers.ModelSerializer):
    children = RecursiveField(many=True, read_only=True, allow_null=True)
    # parent = MenuSerializer.PrimaryKeyRelatedField(queryset=Menu.objects.all(), allow_null=True, required=False)
    parent = ParentMenuSerializer(read_only=True, allow_null=True)

    def validate_parent(self, attrs):
        """
        :return:
        """
        if attrs is None:
            return attrs
        pk = getattr(attrs, 'id')
        name = getattr(attrs, 'name')
        try:
            Menu.objects.get(id=pk, name=name)
        except Menu.DoesNotExist:
            serializers.ValidationError("{0} 父菜单不存在！".format(name))
        return attrs

    class Meta:  # 如果不想每个字段都自己写，那么这就是固定写法，在继承serializer中字段必须自己写，这是二者的区别
        model = Menu  # 指定需要序列化的模型表
        fields = ("__all__")


class RoleSerializer(serializers.ModelSerializer):
    menu = MenuSerializer(
        many=True, read_only=True,
    )
    data_permission = DataPermissionSerializer(
        many=True, read_only=True,
    )

    class Meta:  # 如果不想每个字段都自己写，那么这就是固定写法，在继承serializer中字段必须自己写，这是二者的区别
        model = Role  # 指定需要序列化的模型表
        fields = ("__all__")


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        exclude = ('password',)


class SignInSerializer(serializers.Serializer):
    username = serializers.CharField(
        allow_blank=False,
        allow_null=False,
        error_messages={
            "required": "缺少用户名字段."
        }
    )
    password = serializers.CharField(
        allow_null=False,
        allow_blank=False,
        error_messages={
            "required": "缺少密码字段.",
            "min_length": "密码太短，至少8个字符."
        }
    )

    def validate(self, attrs):
        """
        :param attrs:
        :return:
        """
        user_obj = auth.authenticate(**attrs)
        if not user_obj:
            raise serializers.ValidationError(detail="登录失败，用户名或者密码错误！", code="auth")
        UserInfo.objects.filter(**attrs).update(last_login=datetime.datetime.now())
        return attrs

    def validated_username(self, attrs):
        if not UserInfo.objects.filter(
                username=attrs
        ).exists():
            raise serializers.ValidationError(detail="登录失败，用户不存在！", code="auth")
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    oldPassword = serializers.CharField(allow_blank=False, allow_null=False)
    newPassword = serializers.CharField(allow_blank=False, allow_null=False)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def validate_oldPassword(self, attrs):
        status = auth.authenticate(username=self.user.username, password=attrs)
        if not status:
            raise serializers.ValidationError(detail="密码校验失败！", code="invalid")

    def validate_newPassword(self, attrs):
        """
        :param attrs:
        :return:
        """
        password_validation.validate_password(password=attrs, user=self.user)

    def validate(self, attrs):
        new_password = attrs['newPassword']
        self.user.set_password(new_password)
        self.user.save()
        return attrs


class UserEditRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ("roles",)

    def validated_roles(self, attrs):
        """
        :param attrs:
        :return:
        """
        if not Role.objects.filter(id=attrs).exist():
            raise serializers.ValidationError("角色id不存在:{0}".format(attrs))

    def update(self, instance, validated_data):
        """
        :param instance:
        :param validated_data:
        :return:
        """
        for role in validated_data['roles']:
            instance.roles.add(role)
        instance.save()
        return instance


class UserStatusEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ('is_active',)

    def validated_is_active(self, attrs):
        """
        :param attrs:
        :return:
        """
        if attrs not in [True, False]:
            raise serializers.ValidationError("请输入正确的用户状态值:True,False")
        return attrs

    def update(self, instance, validated_data):
        if not hasattr(instance, 'is_active'):
            raise serializers.ValidationError("object error,必须是Userinfo,才能修改用户状态！")
        instance.is_active = validated_data['is_active']
        instance.save()
        return instance


class RoleMenuEditSerializer(serializers.ModelSerializer):
    menu = serializers.PrimaryKeyRelatedField(
        many=True, required=True, queryset=Menu.objects.all(),
    )

    class Meta:
        model = Role
        fields = ('menu',)

    def update(self, instance, validated_data):
        """
        :param instance:
        :param validated_data:
        :return:
        """
        for permission in validated_data['permissions']:
            instance.menu.add(permission)
        instance.save()
        return instance


__all__ = [
    # 'SubPermissionSerializer',
    'MenuSerializer',
    # 'PermissionSerializer',
    'RoleSerializer',
    'UserInfoSerializer',
    'SignInSerializer',
    'ResetPasswordSerializer',
    'UserEditRoleSerializer',
    'UserStatusEditSerializer',
    'RoleMenuEditSerializer',
    'DataPermissionSerializer'
]
