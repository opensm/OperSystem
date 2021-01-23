# -*- coding: utf-8 -*-
from rest_framework.views import APIView
from Rbac.models import *
from Rbac.backend import ObjectUserInfo
from lib.response import DataResponse
from django.utils import timezone
import datetime
from Rbac.backend import make_token
from Rbac.serializers import \
    RoleSerializer, \
    PermissionSerializer, \
    SignInSerializer, \
    UserInfoSerializer, \
    ResetPasswordSerializer, \
    UserEditRoleSerializer, \
    UserStatusEditSerializer, \
    RolePermissionEditSerializer, \
    RewritePageNumberPagination


def format_error(data):
    if not isinstance(data, dict):
        raise TypeError("数据；类型错误！{0}:{1}".format(type(data), data))

    error_message = ""
    for key, value in data.items():
        if key == "non_field_errors":
            error_message = "{0};{1}".format(error_message, ",".join(value))
        else:
            error_message = "{0}{1}：{2}".format(error_message, key, ",".join(value))
    return error_message


class AuthView(APIView):
    def post(self, request):
        """
        :param request:
        :url api/v1/auth/login
        :parameter:
        {
            "username": "username",
            "password": "password"
        }
        :return:
        """
        data = SignInSerializer(data=request.data)
        if not data.is_valid():
            return DataResponse(
                code='00001',
                msg="登录失败，原因:{0}".format(format_error(data=data.errors))
            )

        # 保存(存在就更新不存在就创建，并设置过期时间为60分钟)
        expiration_time = timezone.now() + timezone.timedelta(minutes=+60)
        token = make_token(username=data.data['username'])
        try:
            other = {
                "username": UserInfo.objects.get(username=data.data['username']),
                "defaults": {
                    "token": token,
                    "expiration_time": expiration_time,
                    "update_date": datetime.datetime.now(),
                }
            }
            UserToken.objects.update_or_create(**other)
            return DataResponse(
                code="00000",
                msg="登录成功!",
                token=token
            )
        except Exception as e:
            return DataResponse(
                code="00001",
                msg="登录失败，用户token更新失败，{0}".format(e)
            )


class LogoutView(APIView):
    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        try:
            UserToken.objects.get(token=token).delete()
            return DataResponse(
                msg='退出登录成功！',
                code='00000'
            )
        except UserToken.DoesNotExist:
            return DataResponse(
                msg="退出登录失败！",
                code='00001'
            )

    def post(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        try:
            UserToken.objects.get(token=token).delete()
            return DataResponse(
                msg='退出登录成功！',
                code='00000'
            )
        except UserToken.DoesNotExist:
            return DataResponse(
                msg="退出登录失败！",
                code='00001'
            )


class RolesView(APIView):

    def get(self, request):
        """
        :param request:
        :url /api/v1/role
        :parameter
        {}
        :return:
        """
        query = Role.objects.all()
        data = RoleSerializer(instance=query, many=True)
        return DataResponse(
            data=data.data,
            msg='获取角色成功！',
            code='00000'
        )

    def post(self, request):
        """
        :param request:
        : url  /api/v1/role:
        :parameter:
        {
            "name": "name",
            "code": "code",
            "desc": "desc"
        }
        :return:
        """
        print(request.data)
        data = RoleSerializer(data=request.data)
        if not data.is_valid():
            print(data.errors)
            return DataResponse(
                msg="添加角色参数异常:{0}".format(format_error(data=data.errors)),
                code='00001'
            )
        else:
            data.save()
            return DataResponse(
                data=data.data,
                msg='角色数据保存成功！',
                code='00000'
            )


class RoleView(APIView):

    def get(self, request, roleId):
        """
        :param request:
        :param roleId:
        :url /api/v1/role/(?P<roleId>[0-9])$
        :parameter:
        {}
        :return: 查看具体角色信息
        """
        try:
            query = Role.objects.get(id=roleId)
        except Role.DoesNotExist:
            return DataResponse(
                msg="获取到角色信息失败,角色ID:{0}".format(roleId),
                code='00001'
            )

        data = RoleSerializer(instance=query)
        return DataResponse(
            data=data.data,
            msg='查看角色信息成功',
            code='00000'
        )

    def put(self, request, roleId):
        """
        :param request:
        :param roleId:
        :url /api/v1/role/(?P<roleId>[0-9])$
        :parameter:
        {
            "name": "name",
            "code": "code",
            "desc": "desc"
        }
        :return: 修改角色信息
        """
        try:
            query = Role.objects.get(id=roleId)
        except Role.DoesNotExist:
            return DataResponse(msg="修改角色信息失败,RoleID:{0}！".format(roleId), code='00001')
        data = RoleSerializer(instance=query, data=request.data)
        if not data.is_valid():
            return DataResponse(msg="修改角色信息失败,RoleID:{0}，{1}！".format(
                roleId, format_error(data=data.errors)
            ), code='00001')
        else:
            data.save()
        return DataResponse(data=data.data, msg='修改角色信息成功', code='00000')

    def delete(self, request, roleId):
        """
        :param request:
        :param roleId:
        :url /api/v1/role/(?P<roleId>[0-9])$
        :parameter:
        {}
        :return: 删除角色
        """
        try:
            Role.objects.get(id=roleId).delete()
            return DataResponse(msg='删除信息成功!', code='00000')
        except Role.DoesNotExist:
            return DataResponse(msg='删除角色失败!', code='00001')


class PermissionsView(APIView):
    def get(self, request, *args, **kwargs):
        """
        :param request:
        :url /api/v1/permissions
        :parameter:
        {}
        :return:
        """
        pg = RewritePageNumberPagination()
        query = Permission.objects.all()
        page_roles = pg.paginate_queryset(queryset=query, request=request, view=self)
        data = PermissionSerializer(instance=page_roles, many=True)
        return pg.get_paginated_response(
            data=data.data,
            msg="获取权限列表成功",
            code='00000'
        )

    def post(self, request):
        """
        :param request:
        :url /api/v1/permission
        :parameter:
        {
            "auth_name": "auth_name",
            "parent": "parent",
            "path": "path",
            "css_style": "css_style",
            "permission_type": "permission_type",
            "request_type": "request_type"
        }
        :return:
        """
        data = PermissionSerializer(data=request.data)
        if not data.is_valid():
            return DataResponse(
                msg='添加数据异常，{0}！'.format(format_error(data=data.errors)),
                code='00001'
            )
        else:
            data.save()
            return DataResponse(
                data=data.data,
                msg='权限数据保存成功！',
                code='00000'
            )


class PermissionView(APIView):

    def get(self, request, permissionId):
        """
        :param request:
        :param permissionId:
        :url /api/v1/permission/<int:permissionId>
        :parameter:
        {}
        :return: 查看权限信息
        """
        try:
            query = Permission.objects.get(id=permissionId)
        except Permission.DoesNotExist:
            return DataResponse(
                msg='查看权限信息失败,PermissionId:{0},原因:不存在！'.format(permissionId),
                code='00001'
            )
        data = PermissionSerializer(instance=query)
        return DataResponse(
            data=data.data,
            msg='查看角色信息成功！',
            code='00000'
        )

    def put(self, request, permissionId):
        """
        :param request:
        :param permissionId:
        :url /api/v1/permission/<int:permissionId>
        :parameter:
        {
            "auth_name": "auth_name",
            "parent": "parent",
            "path": "path",
            "css_style": "css_style",
            "permission_type": "permission_type",
            "request_type": "request_type"
        }
        :return: 修改权限信息
        """

        try:
            query = Permission.objects.get(id=permissionId)
        except Permission.DoesNotExist:
            return DataResponse(
                msg='修改权限失败,权限Id:{0}！'.format(permissionId),
                code='00001'
            )
        data = PermissionSerializer(instance=query, data=request.data)
        if not data.is_valid():
            print(data.errors)
            return DataResponse(
                msg='修改权限失败，{0}！'.format(format_error(data=data.errors)),
                code='00001'
            )
        else:
            data.save()
            return DataResponse(
                data=data.data, msg='修改权限成功！', code='00000'
            )

    def delete(self, request, permissionId):
        """
        :param request:
        :param permissionId:
        :url /api/v1/permission/<int:permissionId>
        :parameter:
        {}
        :return: 删除角色
        """
        if not Permission.objects.filter(id=permissionId).exists():
            return DataResponse(
                msg='权限信息不存在！',
                code='00001'
            )
        try:
            Permission.objects.get(id=permissionId).delete()
            return DataResponse(
                msg='删除权限成功！',
                code='00000'
            )
        except Exception as error:
            return DataResponse(
                msg="删除权限失败:{0}".format(error),
                code='00001'
            )


class UsersView(APIView):

    def get(self, request):
        """
        :param request:
        :url  /api/v1/user
        :parameter:
        {}
        :return: 查看用户列表
        """
        pg = RewritePageNumberPagination()
        query = UserInfo.objects.all()
        page_users = pg.paginate_queryset(queryset=query, request=request, view=self)
        data = UserInfoSerializer(instance=page_users, many=True)
        print(data)
        return pg.get_paginated_response(
            data=data.data,
            msg="获取权限列表成功",
            code='00000'
        )

    def post(self, request):
        """
        :param request:
        :url  /api/v1/user
        :parameter:
        {
            "username": "username",
            "name": "name",
            "mobile": "mobile",
            "email": "email",
            "is_active": "is_active",
            "is_staff": "is_staff"
        }
        :return: 创建用户
        """
        data = UserInfoSerializer(data=request.data)
        if not data.is_valid():
            return DataResponse(
                data=data.data,
                code='00001',
                msg="获取用户列表失败：{0}".format(format_error(data=data.errors))
            )
        else:
            data.save()
            user_data = UserInfo.objects.get(username=data.validated_data['username'])
            user_data.set_password("123456")
            user_data.save()
            return DataResponse(
                data=data.data,
                code='00000',
                msg="角色数据保存成功！"
            )


class UserView(APIView):

    def get(self, request, userId):
        """
        :param request:
        :param userId:
        :url  /api/v1/user/(?P<userId>[0-9])$
        :parameter:
        {}
        :return: 查看具体角色信息
        """
        try:
            query = UserInfo.objects.get(id=userId)
        except UserInfo.DoesNotExist:
            return DataResponse(
                msg="获取到用户信息失败,用户id:{0}!".format(userId),
                code='00001'
            )
        data = UserInfoSerializer(instance=query)
        return DataResponse(
            data=data.data,
            msg="获取到用户信息成功!",
            code='00000'
        )

    def put(self, request, userId):
        """
        :param request:
        :param userId:
        :url  /api/v1/user/(?P<userId>[0-9])$
        :parameter:
        {
            "username": "username",
            "name": "name",
            "mobile": "mobile",
            "email": "email",
            "is_active": "is_active",
            "is_staff": "is_staff"
        }
        :return: 修改用户信息
        """
        try:
            query = UserInfo.objects.get(id=userId)
        except UserInfo.DoesNotExist:
            return DataResponse(
                msg="修改用户信息失败,用户ID:{0}!".format(userId),
                code='00001'
            )
        data = UserInfoSerializer(instance=query, data=request.data)
        if not data.is_valid():
            return DataResponse(
                msg="修改用户信息失败,用户ID:{0},原因:{1}!".format(userId, format_error(data=data.errors)),
                code='00001'
            )
        else:
            data.save()
        return DataResponse(
            data=data.data,
            msg="修改用户信息成功!",
            code='00000'
        )

    def delete(self, request, userId):
        """
        :param request:
        :param userId:
        :url  /api/v1/user/(?P<userId>[0-9])$
        :parameter:
        {}
        :return: 删除用户
        """
        try:
            UserInfo.objects.get(id=userId).delete()
            return DataResponse(
                msg="删除用户信息成功!",
                code='00000'
            )
        except UserInfo.DoesNotExist:
            return DataResponse(
                msg="删除用户信息失败!",
                code='00001'
            )


class ResetPassWordView(APIView):

    def put(self, request, userId):
        """
        :param request:
        :param userId:
        :url  /api/v1/user/(?P<userId>[0-9])/reset_passoword$
        :parameter:
        {
            "oldPassword": "oldPassword",
            "newPassword": "newPassword"
        }
        :return:
        """
        try:
            query = UserInfo.objects.get(id=userId)
        except UserInfo.DoesNotExist:
            return DataResponse(
                msg="获取到用户密码失败,用户ID:{0}!".format(userId),
                code='00001'
            )
        data = ResetPasswordSerializer(user=query, data=request.data)
        if not data.is_valid():
            return DataResponse(
                data=data.data,
                msg="修改密码失败,{0}!".format(format_error(data=data.errors)),
                code='00001'
            )
        else:
            return DataResponse(
                data=data.data,
                msg="修改密码成功!",
                code='00000'
            )


class UserEditRoleView(APIView):

    def put(self, request, userId):
        """
        :param request:
        :param userId:
        :url  /api/v1/user/(?P<userId>[0-9])/roles$
        :parameter:
        {
            "roles": "角色ID1",
            "roles": "角色ID2",
            ......
        }
        :return:
        """
        try:
            query = UserInfo.objects.get(id=userId)
        except UserInfo.DoesNotExist:
            return DataResponse(
                msg="修改到用户关联角色失败,用户ID:{0}!",
                code='00001'
            )
        data = UserEditRoleSerializer(instance=query, data=request.data)
        if not data.is_valid():
            return DataResponse(
                msg="修改到用户关联角色失败,{0}!".format(format_error(data=data.errors)),
                code='00001'
            )
        else:
            data.save()
            return DataResponse(
                msg="修改到用户关联角色成功,用户ID为：{0}".format(userId),
                code='00000'
            )

    def get(self, request, userId):
        """
        :param request:
        :param userId:
        :return:
        """
        try:
            query = UserInfo.objects.get(id=userId)
        except UserInfo.DoesNotExist:
            return DataResponse(
                msg="获取用户角色信息失败,用户ID为:{0}!".format(userId),
                code='00001'
            )
        data = RoleSerializer(instance=query.roles.all(), many=True)
        return DataResponse(
            data=data.data,
            msg="获取用户角色信息成功,用户ID为:{0}!".format(userId),
            code='00000'
        )


class UserStatusEditView(APIView):
    def put(self, request, userId):
        """
        :param request:
        :param userId:
        :url  /api/v1/user/(?P<userId>[0-9])/state$
        :parameter:
        {
            "is_active": "True"|"False",
        }
        :return:
        """
        try:
            query = UserInfo.objects.get(id=userId)
        except UserInfo.DoesNotExist:
            return DataResponse(
                msg="修改用户状态失败,用户ID不存在:{0}!".format(userId),
                code='00001'
            )

        data = UserStatusEditSerializer(instance=query, data=request.data)
        if not data.is_valid():
            return DataResponse(
                msg="修改用户状态失败,{0}!".format(format_error(data=data.errors)),
                code='00001'
            )
        else:
            data.save()
            return DataResponse(
                msg="修改用户状态成功!",
                code='00000'
            )

    def get(self, request, userId):
        """
        :param request:
        :param userId:
        :return:
        """
        try:
            query = UserInfo.objects.get(id=userId)
        except UserInfo.DoesNotExist:
            return DataResponse(
                msg="获取账号状态失败,用户ID:{0}!".format(userId),
                code='00001'
            )
        return DataResponse(
            data={'is_active': query.is_active},
            msg="获取账号状态成功,用户ID:{0}!".format(userId),
            code='00000'
        )


class RolePermissionEditView(APIView):
    def put(self, request, roleId):
        """
        :param request:
        :param roleId:
        :url /api/v1/role/1/permission
        :parameter:
        {
            "permissions": [1,2,3],
        }
        :return:
        """
        try:
            query = Role.objects.get(id=roleId)
        except Role.DoesNotExist:
            return DataResponse(
                msg="获取角色权限信息失败!",
                code='00001'
            )
        data = RolePermissionEditSerializer(instance=query, data=request.data)
        if not data.is_valid():
            return DataResponse(
                msg="修改角色权限信息失败，{0}!".format(format_error(data=data.errors)),
                code='00001'
            )
        else:
            data.save()
            return DataResponse(
                data=data.data,
                msg="修改角色权限成功!",
                code='00000'
            )

    def get(self, request, roleId):
        """
        :param request:
        :param roleId:
        :return:
        """
        try:
            query = Role.objects.get(id=roleId)
        except Role.DoesNotExist:
            return DataResponse(
                code='00001',
                msg="获取角色权限信息失败!"
            )
        data = PermissionSerializer(instance=query, many=True)
        return DataResponse(
            data=data.data,
            code='00000',
            msg='获取角色权限信息失败!'
        )


class CurrentUser(APIView):

    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        token_object = UserToken.objects.get(token=token)
        data = UserInfoSerializer(token_object.username)
        user = ObjectUserInfo()
        menu = data.data
        menu['user_permissions'] = user.get_menu(user_obj=token_object.username)
        return DataResponse(
            data=menu,
            msg="获取当前用户信息成功！",
            code='00000'
        )


class UserMenu(APIView):

    def get(self, request):
        """
        :param request:
        :return:
        """
        token = request.META.get('HTTP_AUTHORIZATION')
        user = ObjectUserInfo()
        user_obj = user.get_user_object(token=token)
        if not user_obj:
            return DataResponse(
                code='00001',
                msg='Token校验失败!'
            )
        menu = user.get_menu(user_obj=user_obj)
        return DataResponse(
            data=menu,
            code='00000',
            msg='获取菜单列表成功!'
        )
