# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _


class Permission(models.Model):
    permission_choice = (
        ("button", "按钮"),
        ("url", "页面"),
        ("menu", "菜单"),
        ('other', "其他")
    )
    request_choice = (
        ("POST", "新增"),
        ("GET", "查看"),
        ("DELETE", "删除"),
        ("PUT", "修改")
    )
    auth_name = models.CharField(verbose_name='权限名称', max_length=32, unique=True)
    parent = models.ForeignKey(
        'self', verbose_name='父级菜单', null=True, blank=True, related_name='children', on_delete=models.DO_NOTHING
    )
    path = models.CharField(verbose_name='URL', max_length=255, null=False, blank=False)
    css_style = models.CharField(
        verbose_name="CSS样式", null=True, blank=True, default="", max_length=2000
    )
    permission_type = models.CharField(
        verbose_name="权限类型", max_length=10, null=False, blank=False, choices=permission_choice,
        default="url"
    )
    request_type = models.CharField(
        verbose_name="请求类型", null=False, default="POST", choices=request_choice, max_length=10
    )
    create_date = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)

    def __str__(self):
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


class UserInfo(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(verbose_name='用户名', max_length=50, null=False, unique=True)
    name = models.CharField(verbose_name="姓名", max_length=50, default='')
    mobile = models.CharField(verbose_name="手机", max_length=12, null=False, default="186000000000")
    roles = models.ManyToManyField(
        Role,
        verbose_name='角色',
        blank=True
    )
    email = models.EmailField(verbose_name="邮箱地址", unique=True, null=False)
    is_active = models.BooleanField(verbose_name="有效", default=True)
    is_staff = models.BooleanField(verbose_name="员工", default=True)
    create_date = models.DateTimeField(verbose_name='创建日期', auto_now_add=True, null=True)
    update_date = models.DateTimeField(verbose_name='更新日期', auto_now_add=True, null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['mobile', 'is_active', 'is_superuser', 'email']

    objects = UserManager()

    class Meta:
        verbose_name_plural = _("User")

    def __str__(self):
        return self.username


class UserToken(models.Model):
    username = models.OneToOneField(to='UserInfo', on_delete=models.DO_NOTHING, verbose_name="用户")
    token = models.CharField(max_length=60)
    update_date = models.DateTimeField(verbose_name='更新日期', auto_now_add=True)
    expiration_time = models.DateTimeField(verbose_name='失效时间', auto_now_add=True)

    class Meta:
        # db_table = 'user_token'
        verbose_name = verbose_name_plural = '用户token表'
