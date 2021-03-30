# -*- coding: utf-8 -*-
from rest_framework.views import APIView
from Rbac.models import *
from lib.response import DataResponse
from django.utils import timezone
# from Rbac.backend import UserResourceQuery
import datetime
from Rbac.backend import make_token
from Rbac.serializers import *
from lib.views import BaseDetailView, BaseListView, BaseGETView, BaseGetPUTView, BasePUTView, UserGETView


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


class ResetPassWordView(BasePUTView):
    model_name = 'UserInfo'
    app_label = 'Rbac'
    serializer_class = ResetPasswordSerializer


class UserEditRoleView(BaseGetPUTView):
    model_name = 'UserInfo'
    app_label = 'Rbac'
    serializer_class = UserEditRoleSerializer


class UserStatusEditView(BaseGetPUTView):
    model_name = 'UserInfo'
    app_label = 'Rbac'
    serializer_class = UserStatusEditSerializer


class RolePermissionEditView(BaseGetPUTView):
    model_name = 'Role'
    app_label = 'Rbac'
    serializer_class = RolePermissionEditSerializer


class CurrentUser(UserGETView):
    model_name = 'UserInfo'
    app_label = 'Rbac'
    serializer_class = RolePermissionEditSerializer


# class UserMenu(APIView):
#
#     def get(self, request):
#         """
#         :param request:
#         :return:
#         """
#         user = UserResourceQuery(request=request)
#         user_obj = user.get_user_model()
#         if not user_obj:
#             return DataResponse(
#                 code='00001',
#                 msg='Token校验失败!'
#             )
#         menu = user.get_menu()
#         return DataResponse(
#             data=menu,
#             code='00000',
#             msg='获取菜单列表成功!'
#         )


class DataPermissionsView(BaseListView):
    model_name = 'DataPermissionRule'
    app_label = 'Rbac'
    serializer_class = DataPermissionSerializer


class DataPermissionView(BaseDetailView):
    model_name = 'DataPermissionRule'
    app_label = 'Rbac'
    serializer_class = DataPermissionSerializer
