import os
import datetime

from django.contrib import auth
from django.contrib.auth import password_validation
from collections import OrderedDict, namedtuple
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
from Rbac.models import Role, Permission, UserInfo
from copy import deepcopy


class RoleSerializer(serializers.ModelSerializer):
    class Meta:  # 如果不想每个字段都自己写，那么这就是固定写法，在继承serializer中字段必须自己写，这是二者的区别
        model = Role  # 指定需要序列化的模型表
        # fields = ("__all__")
        exclude = ('permissions',)


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class SubPermissionSerializer(serializers.ModelSerializer):
    children = RecursiveField(many=True, read_only=True)

    class Meta:  # 如果不想每个字段都自己写，那么这就是固定写法，在继承serializer中字段必须自己写，这是二者的区别
        model = Permission  # 指定需要序列化的模型表
        fields = ('children', 'auth_name', 'resource')

    # def get_fields(self):
    #     fields = super(SubPermissionSerializer, self).get_fields()
    #     print(fields)
    #     fields['children'] = SubPermissionSerializer(many=True)
    #     # print(fields['children'])
    #     return fields


class PermissionSerializer(serializers.ModelSerializer):
    children = RecursiveField(many=True, read_only=True, allow_null=True)

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
        # fields = ("__all__")
        fields = ['children', 'name', 'model', 'path', 'icon', 'level', 'component', 'id']
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
        print(queryset[0])
        print(request.query_params)
        models_queryset = deepcopy(queryset[0])
        for key, value in request.query_params.items():
            if hasattr(queryset[0], key):
                queryset = queryset.filter(**{"{0}__contains".format(key): value})
                print(key, value)
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
