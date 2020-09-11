from rest_framework.serializers import Serializer, ModelSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from Rbac.models import Role, Permission, UserInfo


class RoleSerializer(ModelSerializer):
    class Meta:  # 如果不想每个字段都自己写，那么这就是固定写法，在继承serializer中字段必须自己写，这是二者的区别
        model = Role  # 指定需要序列化的模型表
        # fields = ("__all__")
        exclude = ('permissions',)


class PermissionSerializer(ModelSerializer):
    class Meta:  # 如果不想每个字段都自己写，那么这就是固定写法，在继承serializer中字段必须自己写，这是二者的区别
        model = Permission  # 指定需要序列化的模型表
        # fields = ("__all__")
        exclude = ('create_date',)


class UserInfoSerializer(ModelSerializer):
    class Meta:
        model = UserInfo
        exclude = ('roles', 'create_date', 'update_date')


class SignInSerializer(serializers.Serializer):
    username = serializers.CharField(allow_blank=False, allow_null=False)
    password = serializers.CharField(allow_null=False, allow_blank=False)

    def create(self, validated_data):
        """
        :param validated_data:
        :return:
        """
        print(validated_data)
        return UserInfo(**validated_data)
