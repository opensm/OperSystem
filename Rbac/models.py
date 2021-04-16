# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation


class RequestType(models.Model):
    request = (
        ("POST", "添加"),
        ("GET", "查询"),
        ("DELETE", "删除"),
        ("PATCH", "修改")
    )
    name = models.CharField(verbose_name="操作类型", max_length=50, default="")
    method = models.CharField(
        verbose_name="请求类型",
        default="POST",
        max_length=7,
        choices=request,
        null=True
    )

    class Meta:
        db_table = 'sys_request_type'


class Menu(models.Model):
    menu_choice = (
        (0, "一级菜单"),
        (1, "二级菜单"),
        (2, "三级菜单"),
        (999, "按钮功能")
    )
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name="菜单名称", max_length=50, null=False, blank=False, unique=True)
    path = models.CharField(verbose_name="URL", max_length=200, null=False, blank=False, unique=True)
    parent = models.ForeignKey('self', verbose_name='父级菜单', null=True, blank=True, related_name='children',
                               on_delete=models.DO_NOTHING)
    icon = models.CharField(verbose_name="图标", max_length=50, null=True, blank=True, default="")
    index = models.IntegerField(verbose_name='菜单序列', null=False, blank=False, default=0)
    permission = models.ForeignKey(verbose_name="数据权限", default=None, to="DataPermissionRule",
                                   on_delete=models.DO_NOTHING)
    level = models.IntegerField(verbose_name="菜单级别", default=0, choices=menu_choice)
    create_date = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)

    class Meta:
        unique_together = (('parent', 'index'),)
        db_table = 'sys_menus'


# class Permission(models.Model):
#     name = models.CharField(verbose_name='权限名称', max_length=32, unique=True)
#     model = models.OneToOneField('DataPermissionRule', default=None, blank=True, on_delete=models.DO_NOTHING)
#     path = models.CharField(
#         verbose_name='URL', max_length=255, null=False, blank=False, default="/", unique=True
#     )
#     create_date = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)
#
#     class Meta:
#         db_table = 'sys_permissions'
#
#     def __str__(self):
#         return self.name


class Role(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='角色', max_length=32, blank=False, null=False, default="默认角色")
    desc = models.TextField(verbose_name="角色描述", blank=True)
    menu = models.ManyToManyField(
        Menu,
        verbose_name='Menu',
        blank=True,
    )
    data_permission = models.ManyToManyField(
        "DataPermissionRule",
        blank=True
    )

    class Meta:
        db_table = 'sys_roles'


class DataPermissionRule(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        verbose_name="规则名称", max_length=10, default='默认规则'
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING, verbose_name="关联模型", default=0)
    request_type = models.ManyToManyField(RequestType, verbose_name="请求类型", default=0)

    class Meta:
        db_table = 'sys_permission_rule'


class DataPermissionList(models.Model):
    operate_choice = (
        ("eq", "等于")
    )
    id = models.AutoField(primary_key=True)
    permission_rule = models.ManyToManyField(verbose_name="数据权限规则", to="DataPermissionRule")
    operate_type = models.CharField(default="eq", max_length=20, verbose_name="运算规则", null=False)
    value = models.CharField(verbose_name="值", default="", max_length=20)
    check_field = models.CharField(verbose_name="校验的字段", max_length=20, default="pk", null=True)

    class Meta:
        db_table = 'sys_data_permission_list'
        unique_together = (('check_field', 'value'),)


class UserInfo(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    username = models.CharField(verbose_name='用户名', max_length=50, null=False, unique=True)
    name = models.CharField(verbose_name="姓名", max_length=50, default='')
    mobile = models.CharField(verbose_name="手机", max_length=12, null=False, default="186000000000")
    roles = models.ManyToManyField(
        Role,
        verbose_name='角色'
    )
    email = models.EmailField(verbose_name="邮箱地址", unique=True, null=False)
    is_active = models.BooleanField(verbose_name="有效", default=True)
    is_staff = models.BooleanField(verbose_name="员工", default=True)
    create_date = models.DateTimeField(verbose_name='创建日期', auto_now_add=True, null=True)
    update_date = models.DateTimeField(verbose_name='更新日期', auto_now_add=True, null=True)
    last_login = models.DateTimeField(verbose_name='最近登录', auto_now_add=True, null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['mobile', 'is_active', 'is_superuser', 'email']

    objects = UserManager()

    class Meta:
        db_table = 'sys_users'
        verbose_name_plural = _("User")

    def __str__(self):
        return self.username


class UserToken(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.OneToOneField(
        to='UserInfo', on_delete=models.DO_NOTHING,
        verbose_name="用户", default=0
    )
    token = models.CharField(max_length=60)
    update_date = models.DateTimeField(verbose_name='更新日期', default=0)
    expiration_time = models.DateTimeField(verbose_name='失效时间', default=0)

    class Meta:
        db_table = 'sys_token'
        verbose_name = verbose_name_plural = '用户token表'
