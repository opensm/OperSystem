from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.contrib import auth
from django.contrib.auth import password_validation
from Rbac.models import Role, Permission, UserInfo
import os


class RoleSerializer(ModelSerializer):
    class Meta:  # 如果不想每个字段都自己写，那么这就是固定写法，在继承serializer中字段必须自己写，这是二者的区别
        model = Role  # 指定需要序列化的模型表
        # fields = ("__all__")
        exclude = ('permissions',)


class PermissionSerializer(ModelSerializer):

    def validate(self, attrs):
        """
        :param attrs:
        :return:
        """
        path_length = len(attrs['path'].split(os.sep))
        print(os.sep)
        print(attrs['path'].split(os.sep))
        print(attrs['path'])
        if attrs['permission_type'] in ('url', 'button') and not attrs['path']:
            raise serializers.ValidationError("当权限类型为:url或者button,权限的地址必须存在")
        if attrs['permission_type'] == 'menu' and attrs['path']:
            raise serializers.ValidationError("当权限为:menu,权限内容必须为空")
        if attrs['path'].startswith(os.sep) and path_length < 2:
            raise serializers.ValidationError("输入权限格式错误！")
        if path_length > 1 and attrs['parent'] is not None:
            raise serializers.ValidationError("当权限为完整路径，则父权限应该为空")
        if path_length > 1 and attrs['level'] != 999:
            raise serializers.ValidationError("获取到权限为完整路径，权限等级应该为:999！")
        return attrs

    def validate_permission_type(self, attrs):
        """
        :param attrs:
        :return:
        """
        if attrs not in ("button", "menu", "url"):
            raise serializers.ValidationError("传入的权限类型错误，权限类型必须为:button,menu,url")
        return attrs

    class Meta:  # 如果不想每个字段都自己写，那么这就是固定写法，在继承serializer中字段必须自己写，这是二者的区别
        model = Permission  # 指定需要序列化的模型表
        # fields = ("__all__")
        exclude = ('create_date',)


class UserInfoSerializer(ModelSerializer):
    class Meta:
        model = UserInfo
        exclude = ('password',)
        # fields = '__all__'


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
