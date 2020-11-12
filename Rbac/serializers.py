import os
import datetime

from django.contrib import auth
from django.contrib.auth import password_validation
from rest_framework import serializers

from Rbac.models import Role, Permission, UserInfo


class RoleSerializer(serializers.ModelSerializer):
    class Meta:  # 如果不想每个字段都自己写，那么这就是固定写法，在继承serializer中字段必须自己写，这是二者的区别
        model = Role  # 指定需要序列化的模型表
        # fields = ("__all__")
        exclude = ('permissions',)


class RecursiveField(serializers.Serializer):
    def to_native(self, value):
        return self.parent.to_native(value)


class SubPermissionSerializer(serializers.ModelSerializer):
    # parent = RecursiveField(many=True)

    class Meta:  # 如果不想每个字段都自己写，那么这就是固定写法，在继承serializer中字段必须自己写，这是二者的区别
        model = Permission  # 指定需要序列化的模型表
        fields = ('children', 'auth_name', 'resource')

    def get_fields(self):
        fields = super(SubPermissionSerializer, self).get_fields()
        print(fields)
        fields['children'] = SubPermissionSerializer(many=True)
        # print(fields['children'])
        return fields


class PermissionSerializer(serializers.ModelSerializer):
    # children = SubPermissionSerializer(many=True)

    def validate(self, attrs):
        """
        :param attrs:
        :return:
        """
        path_length = len(attrs['path'].split(os.sep))
        # /api/v1/auth/login button post
        if (attrs['path'].startswith(os.sep) and path_length > 1) and attrs['is_menu']:
            raise serializers.ValidationError("当权限为完整的列表时，权限不能为menu,或者当权限为menu时，权限不能为完整列表")
        # if attrs['permission_type'] in ('url', 'button') and not attrs['path']:
        #     raise serializers.ValidationError("当权限类型为:url或者button,权限的地址必须存在")
        # if attrs['path'].startswith(os.sep) and path_length < 2:
        #     raise serializers.ValidationError("输入权限格式错误！")
        # if path_length > 1 and attrs['parent'] is not None:
        #     raise serializers.ValidationError("当权限为完整路径，则父权限应该为空")
        # if path_length > 1 and attrs['permission_type'] != "other":
        #     raise serializers.ValidationError("获取到权限为完整路径，权限等级应该为:999！")
        # if path_length < 2 and attrs['permission_type'] == "other":
        #     raise serializers.ValidationError("输入的权限等级，与权限不一致！")
        # if attrs['permission_type'] != "other" and attrs['path'] is None:
        #     raise serializers.ValidationError("权限等级不为：999，请输入权限")
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
        fields = ("__all__")
        # fields = ['children', 'auth_name', 'path', 'css_style', 'is_menu', 'request_type']
        # exclude = ('create_date',)
        read_only_fields = ['id']


class UserInfoSerializer(serializers.ModelSerializer):
    # permissions = serializers.PrimaryKeyRelatedField(
    #     many=True, required=True, queryset=Permission.objects.all(),
    # )

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


class RolePermissionEditSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(
        many=True, required=True, queryset=Permission.objects.all(),
    )

    class Meta:
        model = Role
        fields = ('permissions',)

    def update(self, instance, validated_data):
        """
        :param instance:
        :param validated_data:
        :return:
        """
        # instance.permissions.clean()
        for permission in validated_data['permissions']:
            instance.permissions.add(permission)
        instance.save()
        return instance
