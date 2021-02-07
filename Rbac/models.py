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


class Permission(models.Model):
    menu_choice = (
        (0, "一级菜单"),
        (1, "二级菜单"),
        (2, "三级菜单"),
        (3, "四级菜单"),
        (4, "五级菜单"),
        (999, "按钮功能")
    )
    name = models.CharField(verbose_name='权限名称', max_length=32, unique=True)
    parent = models.ForeignKey(
        'self',
        verbose_name='父级菜单',
        null=True,
        blank=True,
        related_name='children',
        on_delete=models.DO_NOTHING
    )
    # model = models.CharField(
    #     verbose_name='相关资源', max_length=255, null=False, blank=False, default="login", unique=True
    # )
    model = models.ManyToManyField('DataPermission', default=None, blank=True)
    path = models.CharField(
        verbose_name='URL', max_length=255, null=False, blank=False, default="/", unique=True
    )
    icon = models.CharField(
        verbose_name="图标", null=True, blank=True, default="", max_length=50
    )
    index = models.IntegerField(
        verbose_name='菜单序列', null=False, blank=False, default=0, unique=True
    )
    hidden = models.BooleanField(verbose_name="是否显示", default=False)
    level = models.IntegerField(verbose_name="菜单级别", default=0, choices=menu_choice)
    create_date = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)

    class Meta:
        unique_together = (('parent', 'index'),)
        db_table = 'sys_permissions'

    def __str__(self):
        return self.name


class DataPermission(models.Model):
    check_type = (
        ("all", "全部数据"),
        ("pk", "唯一键"),
        ("field", "字段")
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
    data_check_type = models.CharField(
        verbose_name="校验数据权限类型", max_length=10, default='pk', choices=check_type
    )
    check_field = models.CharField(verbose_name="校验的字段", max_length=20, default="pk", null=True)

    class Meta:
        db_table = 'sys_data_permission'


class Role(models.Model):
    name = models.CharField(verbose_name='角色', max_length=32, blank=False, null=False, default="默认角色")
    desc = models.TextField(verbose_name="角色描述", blank=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name='permissions',
        blank=True,
    )

    class Meta:
        db_table = 'sys_roles'


class DataPermissionList(models.Model):
    check_type = (
        ("all", "全部数据"),
        ("pk", "唯一键"),
        ("field", "字段")
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
    # model = models.ForeignKey(DataPermission, default="all", on_delete=models.DO_NOTHING)
    # value = models.CharField(verbose_name="权限值对应的列表", default="", max_length=20)
    request_type = models.ManyToManyField(RequestType, verbose_name="请求类型", default=0)
    role = models.ManyToManyField(Role, default=0)
    data_check_type = models.CharField(
        verbose_name="校验数据权限类型", max_length=10, default='pk', choices=check_type
    )
    object_id = models.PositiveIntegerField()
    check_field = models.CharField(verbose_name="校验的字段", max_length=20, default="pk", null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        db_table = 'sys_data_permission_list'
        # unique_together = (('content_type', 'content_object', 'role', 'request_type'),)


class UserInfo(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(verbose_name='用户名', max_length=50, null=False, unique=True)
    name = models.CharField(verbose_name="姓名", max_length=50, default='')
    mobile = models.CharField(verbose_name="手机", max_length=12, null=False, default="186000000000")
    roles = models.ForeignKey(
        Role,
        verbose_name='角色',
        blank=True,
        null=True,
        on_delete=models.CASCADE
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
