import datetime
from django.contrib import auth
from django.contrib.auth import password_validation
from django.contrib.contenttypes.models import ContentType
from Rbac.models import Role, UserInfo, DataPermissionRule, Menu, RequestType, DataPermissionList
from rest_framework import serializers


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class RequestTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestType
        fields = "__all__"


class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = "__all__"


class DataPermissionSerializer(serializers.ModelSerializer):
    app_label_set = serializers.CharField(source='content_type.app_label', read_only=True)
    model_set = serializers.CharField(source='content_type.model', read_only=True)

    class Meta:
        model = DataPermissionRule
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.user = None
        if 'user' in kwargs:
            kwargs.pop('user')
        super(DataPermissionSerializer, self).__init__(*args, **kwargs)


class DataPermissionListSerializer(serializers.ModelSerializer):
    permission_rule_set = serializers.CharField(source='permission_rule.name', read_only=True)
    permission_rule_request_set = serializers.SlugRelatedField(
        source='permission_rule.request_type.all',
        many=True,
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = DataPermissionList
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.user = None
        if 'user' in kwargs:
            kwargs.pop('user')
        super(DataPermissionListSerializer, self).__init__(*args, **kwargs)


class SubMenuSerializer(serializers.ModelSerializer):
    class Meta:  # 如果不想每个字段都自己写，那么这就是固定写法，在继承serializer中字段必须自己写，这是二者的区别
        model = Menu  # 指定需要序列化的模型表
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.user = None
        if 'user' in kwargs:
            kwargs.pop('user')
        super(SubMenuSerializer, self).__init__(*args, **kwargs)


class MenuSerializer(serializers.ModelSerializer):
    children = RecursiveField(many=True, read_only=True, allow_null=True)

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

    def update(self, instance, validated_data):
        if not isinstance(validated_data, dict):
            raise serializers.ValidationError("输入数据类型错误！")
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    class Meta:  # 如果不想每个字段都自己写，那么这就是固定写法，在继承serializer中字段必须自己写，这是二者的区别
        model = Menu  # 指定需要序列化的模型表
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.user = None
        if 'user' in kwargs:
            kwargs.pop('user')
        super(MenuSerializer, self).__init__(*args, **kwargs)


class RoleSerializer(serializers.ModelSerializer):
    class Meta:  # 如果不想每个字段都自己写，那么这就是固定写法，在继承serializer中字段必须自己写，这是二者的区别
        model = Role  # 指定需要序列化的模型表
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.user = None
        if 'user' in kwargs:
            kwargs.pop('user')
        super(RoleSerializer, self).__init__(*args, **kwargs)


class UserInfoSerializer(serializers.ModelSerializer):
    role_set = serializers.CharField(source='roles.name', read_only=True, default='超级用户')

    class Meta:
        model = UserInfo
        exclude = ('password',)

    def create(self, validated_data):
        """
        :param validated_data:
        :return:
        """
        obj = UserInfo.objects.create(**validated_data)
        obj.set_password('Abc@1234')
        obj.save()
        return obj

    def __init__(self, *args, **kwargs):
        self.user = None
        if 'user' in kwargs:
            kwargs.pop('user')
        super(UserInfoSerializer, self).__init__(*args, **kwargs)


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
    oldPassword = serializers.CharField()
    password = serializers.CharField(allow_blank=False, allow_null=False)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def validate_oldPassword(self, attrs):
        if not self.user.check_password(attrs):
            raise serializers.ValidationError('密码不正确')
        return attrs

    def validate_password(self, attrs):
        """
        :param attrs:
        :return:
        """
        password_validation.validate_password(password=attrs, user=self.user)
        return attrs
    # def validate(self, attrs):
    #     password = attrs['password']
    #     self.user.set_password(password)
    #     u = UserInfo.objects.filter(username=self.user.username).update(password=self.user.password)
    #     # print(u.password)
    #     # print(u.set_password(password))
    #     # print(u.password)
    #     # u.save()
    #     return attrs

    # def create(self, validated_data):
    #     new_password = validated_data['password']
    #     self.user.set_password(new_password)
    #     print(self.user.id)
    #     print(self.user.username)
    #     print(self.)
    #     self.user.save()
    #     return None


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
    'ContentTypeSerializer',
    'MenuSerializer',
    # 'PermissionSerializer',
    'RoleSerializer',
    'UserInfoSerializer',
    'SignInSerializer',
    'ResetPasswordSerializer',
    'UserEditRoleSerializer',
    'UserStatusEditSerializer',
    'RoleMenuEditSerializer',
    'DataPermissionSerializer',
    'DataPermissionListSerializer',
    'SubMenuSerializer'
]
