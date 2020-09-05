# -*- coding: utf-8 -*-
from django.db import models
# from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _


# Create your models here.


class Permission(models.Model):
    code_choice = {
        ("insert", "添加"),
        ("delete", "删除"),
        ("select", "查看"),
        ("update", "修改")
    }
    title = models.CharField(verbose_name='权限名称', max_length=32, unique=True)
    parent = models.ForeignKey(
        'self', verbose_name='父级菜单', null=True, blank=True, related_name='children', on_delete=models.DO_NOTHING
    )
    code = models.CharField(verbose_name="读写情况", choices=code_choice, default="select", max_length=50)
    url = models.CharField(verbose_name='URL', max_length=255)
    is_menu = models.BooleanField(verbose_name='是否是菜单')
    create_date = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)

    def __str__(self):
        return self.title


class Role(models.Model):
    name = models.CharField(verbose_name='角色', max_length=32, blank=True, null=True)
    code = models.CharField(verbose_name='编码', max_length=32, blank=True, null=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name='permissions',
        blank=True,
    )


class UserInfo(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(verbose_name='用户名', max_length=50, null=False, unique=True)
    name = models.CharField(verbose_name="姓名", max_length=50, default='')
    mobile = models.CharField(verbose_name="手机", max_length=11, blank=True, null=True)
    roles = models.ManyToManyField(
        Role,
        verbose_name='角色',
        blank=True,
    )
    email = models.EmailField(verbose_name="邮箱地址", unique=True)
    is_active = models.BooleanField(verbose_name="有效", default=True)
    is_staff = models.BooleanField(verbose_name="员工", default=True)
    create_date = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)
    update_date = models.DateTimeField(verbose_name='更新日期', auto_now_add=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['mobile', 'department', 'is_active', 'is_superuser', 'roles']

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
        db_table = 'user_token'
        verbose_name = verbose_name_plural = '用户token表'
