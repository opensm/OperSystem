# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _


class Permission(models.Model):
    menu_choice = (
        (0, "一级菜单"),
        (1, "二级菜单"),
        (2, "三级菜单"),
        (999, "按钮功能")
    )
    request = (
        ("POST", "添加"),
        ("GET", "查询"),
        ("DELETE", "删除"),
        ("PATCH", "修改")
    )
    auth_name = models.CharField(verbose_name='权限名称', max_length=32, unique=True)
    parent = models.ForeignKey(
        'self',
        verbose_name='父级菜单',
        null=True,
        blank=True,
        related_name='children',
        on_delete=models.DO_NOTHING
    )
    resource = models.CharField(
        verbose_name='相关资源', max_length=255, null=False, blank=False, default="login", unique=True
    )
    path = models.CharField(
        verbose_name='URL', max_length=255, null=False, blank=False, default="/", unique=True
    )
    css = models.CharField(
        verbose_name="CSS样式", null=True, blank=True, default="", max_length=2000
    )
    level = models.IntegerField(verbose_name="菜单级别", default=0, choices=menu_choice)
    method = models.CharField(
        verbose_name="请求类型",
        default="POST",
        max_length=7,
        choices=request,
        null=True
    )
    create_date = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)

    class Meta:
        unique_together = (("resource", "method"), ("path", "method"), ("resource", "path"))

    def __str__(self):
        db_table = 'sys_permissions'
        return self.auth_name


class Role(models.Model):
    name = models.CharField(verbose_name='角色', max_length=32, blank=False, null=False, default="默认角色")
    code = models.CharField(verbose_name='编码', max_length=32, blank=False, null=False, default="master")
    desc = models.TextField(verbose_name="角色描述", blank=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name='permissions',
        blank=True,
    )

    class Meta:
        db_table = 'sys_roles'


class UserInfo(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(verbose_name='用户名', max_length=50, null=False, unique=True)
    name = models.CharField(verbose_name="姓名", max_length=50, default='')
    mobile = models.CharField(verbose_name="手机", max_length=12, null=False, default="186000000000")
    roles = models.ForeignKey(
        Role,
        verbose_name='角色',
        blank=True,
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
        to='UserInfo', on_delete=models.DO_NOTHING, verbose_name="用户"
    )
    token = models.CharField(max_length=60)
    update_date = models.DateTimeField(verbose_name='更新日期', auto_now_add=True)
    expiration_time = models.DateTimeField(verbose_name='失效时间', auto_now_add=True)

    class Meta:
        db_table = 'sys_token'
        verbose_name = verbose_name_plural = '用户token表'
