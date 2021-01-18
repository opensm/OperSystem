import datetime
from django.contrib import auth
from django.contrib.auth import password_validation
from collections import OrderedDict
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
from Rbac.models import Role, Permission, UserInfo
from copy import deepcopy


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class SubPermissionSerializer(serializers.ModelSerializer):
    class Meta:  # 如果不想每个字段都自己写，那么这就是固定写法，在继承serializer中字段必须自己写，这是二者的区别
        model = Permission  # 指定需要序列化的模型表
        fields = ('name', 'id')


class PermissionSerializer(serializers.ModelSerializer):
    children = RecursiveField(many=True, read_only=True, allow_null=True)
    parent = SubPermissionSerializer()

    class Meta:  # 如果不想每个字段都自己写，那么这就是固定写法，在继承serializer中字段必须自己写，这是二者的区别
        model = Permission  # 指定需要序列化的模型表
        fields = ("__all__")
        read_only_fields = ['id', 'parent']

    def validate_parent(self, attrs):
        """
        :return:
        """
        serializers.ValidationError("DDDDDD")
        print("++++++++++++++++++++++++++++++++")
        print(attrs)
        print("++++++++++++++++++++++++++++++++")
        # try:
        #     Permission.objects.get(id=attrs['id'], name=attrs['name'])
        # except Permission.DoesNotExist:
        #     serializers.ValidationError("{0} 父菜单不存在！".format(attrs['name']))
        return attrs

    def update(self, instance, validated_data):
        print("-------------------------------")
        print(validated_data)
        print("-------------------------------")
        # parent = validated_data.pop('parent')
        # instance.parent = parent
        return instance


class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

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


# 自定义分页类
class RewritePageNumberPagination(PageNumberPagination):
    # 每页显示多少个
    page_size = 10
    # 默认每页显示3个，可以通过传入pager1/?page=2&size=4,改变默认每页显示的个数
    page_size_query_param = "size"
    # 最大页数不超过10
    max_page_size = 1000
    # 获取页码数的
    page_query_param = "page"
    sort_query_param = "sort"

    def get_paginated_response(self, data, msg=None, code="00000"):
        """
        :param data:
        :param msg:
        :param code:
        :return:
        """
        if msg is None:
            raise ValueError("msg不能为空")
        if not isinstance(code, str):
            raise TypeError('code 类型错误，必须是string')
        meta = {'msg': msg, 'code': code}
        return Response(OrderedDict([
            ('total', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('data', data),
            ('meta', meta),
            ('pagesize', self.page.has_other_pages())
        ]))

    def paginate_queryset(self, queryset, request, view=None):
        """
        :param queryset:
        :param request:
        :param view:
        :return:
        """
        models_queryset = deepcopy(queryset[0])
        params = dict()
        for field in models_queryset._meta.fields:
            for key, value in request.query_params.items():
                if field.name != key:
                    continue
                if type(field).__name__ in ['CharField', 'Textfield']:
                    params["{0}__contains".format(key)] = value
                else:
                    params[key] = value
        # if len(params) > 0:
        print(params)
        print(queryset)
        queryset = queryset.filter(**params)
        sort_by = request.query_params.get(self.sort_query_param, '+id').strip('+')
        if not hasattr(queryset, sort_by.strip('-')) and sort_by.strip('-') != 'id':
            raise ValueError(
                '不包含字段:{0}'.format(sort_by)
            )
        return super(RewritePageNumberPagination, self).paginate_queryset(
            queryset=queryset.order_by(sort_by),
            request=request,
            view=view
        )


class LimitRewritePageNumberPagination(LimitOffsetPagination):
    default_limit = 5  # 前台不传每页默认显示条数

    limit_query_param = 'page'  # 前天控制每页的显示条数查询参数，一般不需要改，系统默认为 limit 变量
    offset_query_param = 'offset'  # 前天控制从哪一条开始显示的查询参数
    # eg:http://127.0.0.1: 8122/book/?xx=5&offset=7  表示显示第8条开始，往下显示5条记录
    max_limit = 10  # 后台控制显示的最大条数防止前台输入数据过大

    def get_paginated_response(self, data, msg=None, code="00000"):
        """
        :param data:
        :param msg:
        :param code:
        :return:
        """
        if msg is None:
            raise ValueError("msg不能为空")
        if not isinstance(code, str):
            raise TypeError('code 类型错误，必须是string')
        meta = {'msg': msg, 'code': code}
        return Response(OrderedDict([
            ('total', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('data', data),
            ('meta', meta)
        ]))
