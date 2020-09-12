from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.contrib import auth
from Rbac.models import Role, Permission, UserInfo, UserToken
import hashlib
import datetime
import time
from KubernetesManagerWeb.settings import SECRET_KEY


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
        # exclude = ('roles', 'create_date', 'update_date')
        fields = '__all__'


class SignInSerializer(serializers.Serializer):
    username = serializers.CharField(allow_blank=False, allow_null=False)
    password = serializers.CharField(allow_null=False, allow_blank=False)

    def login(self, **validated_data):
        """
        :param validated_data:
        :return:
        """
        user_obj = auth.authenticate(**validated_data)
        try:
            if user_obj:
                md5 = hashlib.md5(
                    "{0}{1}{2}".format(validated_data['username'], time.time(), SECRET_KEY).encode("utf8"))
                token = md5.hexdigest()
                # 保存(存在就更新不存在就创建，并设置过期时间为60分钟)
                expiration_time = datetime.datetime.now() + datetime.timedelta(minutes=60)
                defaults = {
                    "token": token,
                    "expiration_time": expiration_time,
                    "update_date": datetime.datetime.now()
                }
                UserToken.objects.update_or_create(username=user_obj, defaults=defaults)
                res = {
                    "data": "null",
                    "token": token,
                    "meta": {"msg": "登录成功！", "status": 200}
                }
                return res
            else:
                res = {
                    "data": "null",
                    "token": "null",
                    "meta": {"msg": "登录失败,用户不存在，或者验证失败！", "status": 401}
                }
            return res

        except Exception as error:
            res = {
                "data": "null",
                "token": "null",
                "meta": {"msg": "内部错误:{0}".format(error), "status": 500}
            }
            return res
