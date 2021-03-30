# -*- coding: utf-8 -*-
from rest_framework.views import APIView
from Rbac.models import *
from lib.response import DataResponse
from django.utils import timezone
from Rbac.backend import UserResourceQuery
import datetime
from Rbac.backend import make_token
from Rbac.serializers import *
from lib.views import BaseDetailView, BaseListView


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


class RolesView(BaseListView):
    serializer_class = RoleSerializer
    model_name = 'Role'
    app_label = 'Rbac'


class RoleView(BaseDetailView):
    model_name = 'Role'
    app_label = 'Rbac'
    serializer_class = RoleSerializer


class PermissionsView(BaseListView):
    model_name = 'Permission'
    app_label = 'Rbac'
    serializer_class = PermissionSerializer


class PermissionView(BaseDetailView):
    model_name = 'Permission'
    app_label = 'Rbac'
    serializer_class = PermissionSerializer


class UsersView(BaseListView):
    model_name = 'UserInfo'
    app_label = 'Rbac'
    serializer_class = UserInfoSerializer


class UserView(BaseDetailView):
    model_name = 'Permission'
    app_label = 'Rbac'
    serializer_class = UserInfoSerializer


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
        user = UserResourceQuery(request=request)
        menu = data.data
        menu['user_permissions'] = user.get_menu()
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
        user = UserResourceQuery(request=request)
        user_obj = user.get_user_model()
        if not user_obj:
            return DataResponse(
                code='00001',
                msg='Token校验失败!'
            )
        menu = user.get_menu()
        return DataResponse(
            data=menu,
            code='00000',
            msg='获取菜单列表成功!'
        )


class DataPermissionsView(BaseListView):
    model_name = 'DataPermissionRule'
    app_label = 'Rbac'
    serializer_class = DataPermissionSerializer


class DataPermissionView(BaseDetailView):
    model_name = 'DataPermissionRule'
    app_label = 'Rbac'
    serializer_class = DataPermissionSerializer
