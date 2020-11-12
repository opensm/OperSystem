# -*- coding: utf-8 -*-
from rest_framework.views import APIView
from Rbac.models import *
from Rbac.backend import ObjectUserInfo
from django.http import JsonResponse
from django.utils import timezone
import hashlib
import datetime
import time
from KubernetesManagerWeb.settings import SECRET_KEY
from Rbac.serializers import \
    RoleSerializer, \
    PermissionSerializer, \
    SignInSerializer, \
    UserInfoSerializer, \
    ResetPasswordSerializer, \
    UserEditRoleSerializer, \
    UserStatusEditSerializer, \
    RolePermissionEditSerializer, \
    SubPermissionSerializer


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
            format_error(data=data.errors)
            res = {
                "data": "null",
                "meta": {"msg": format_error(data=data.errors).lstrip(';'), "status": 401}
            }
            return JsonResponse(res)
        md5 = hashlib.md5(
            "{0}{1}{2}".format(data.data['username'], time.time(), SECRET_KEY).encode("utf8")
        )
        token = md5.hexdigest()
        # 保存(存在就更新不存在就创建，并设置过期时间为60分钟)
        expiration_time = timezone.now() + timezone.timedelta(minutes=+60)
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
            res = {
                "data": "null",
                "token": token,
                "meta": {"msg": "登录成功！", "status": 200}
            }
            return JsonResponse(res)
        except Exception as error:
            res = {
                "data": "null",
                "meta": {"msg": "登录失败，用户token更新失败，{0}".format(error), "status": 500}
            }
            return JsonResponse(res)


class LogoutView(APIView):
    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        try:
            UserToken.objects.get(token=token).delete()
            res = {
                "data": [],
                "meta": {"msg": "退出登录成功！", "status": 200}
            }
            return JsonResponse(res)
        except Exception as error:
            res = {
                "data": [],
                "meta": {"msg": "退出登录失败，{0}！".format(error), "status": 500}
            }
            return JsonResponse(res)

    def post(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        try:
            UserToken.objects.get(token=token).delete()
            res = {
                "data": [],
                "meta": {"msg": "退出登录成功！", "status": 200}
            }
            return JsonResponse(res)
        except Exception as error:
            res = {
                "data": [],
                "meta": {"msg": "退出登录失败，{0}！".format(error), "status": 500}
            }
            return JsonResponse(res)


class RolesView(APIView):

    def get(self, request):
        """
        :param request:
        :url /api/v1/role
        :parameter
        {}
        :return:
        """
        try:
            query = Role.objects.all()
            data = RoleSerializer(instance=query, many=True)
            res = {
                "data": data.data,
                "meta": {"msg": "获取角色成功", "status": 200}
            }
            return JsonResponse(res)
        except Exception as error:
            res = {
                "data": "null",
                "token": "null",
                "meta": {"msg": "内部错误:{0}".format(error), "status": 500}
            }
            return JsonResponse(res)

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
        data = RoleSerializer(data=request.data)
        if not data.is_valid():
            res = {
                "data": "null",
                "meta": {"msg": "传入参数错误:{0}".format(format_error(data=data.errors)), "status": 500}
            }
            return JsonResponse(res)
        else:
            data.save()
            res = {
                "data": data.data,
                "meta": {"msg": "角色数据保存成功", "status": 200}
            }
            return JsonResponse(res)


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
        except Exception as error:
            res = {
                "data": "null",
                "meta": {"msg": "获取到角色信息失败,RoleID:{0},原因:{1}".format(roleId, error), "status": 500}
            }
            return JsonResponse(res)

        data = RoleSerializer(instance=query)
        res = {
            "data": data.data,
            "meta": {"msg": "查看角色信息成功", "status": 200}
        }
        return JsonResponse(res)

    def post(self, request):
        """
        :param request:
        :return:修改角色权限分配
        """
        return JsonResponse({"data": "post"})

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
        except Exception as error:
            res = {
                "data": "null",
                "meta": {"msg": "修改角色信息失败,RoleID:{0},原因:{1}".format(roleId, error), "status": 500}
            }
            return res
        data = RoleSerializer(instance=query, data=request.data)
        if not data.is_valid():
            res = {
                "data": data.data,
                "meta": {"msg": "传入参数错误:{0}".format(format_error(data=data.errors)), "status": 500}
            }
            return JsonResponse(res)
        else:
            data.save()
            res = {
                "data": data.data,
                "meta": {"msg": "修改角色信息成功", "status": 200}
            }
        return JsonResponse(res)

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
            res = {
                "data": request.data,
                "meta": {"msg": "删除信息成功！", "status": 200}
            }
            return JsonResponse(res)
        except Exception as error:
            res = {
                "data": "null",
                "meta": {"msg": "删除角色失败:{0}".format(error), "status": 500}
            }
            return JsonResponse(res)


class PermissionsView(APIView):
    def get(self, request):
        """
        :param request:
        :url /api/v1/permission
        :parameter:
        {}
        :return:
        """
        try:
            query = Permission.objects.all()
            data = PermissionSerializer(instance=query, many=True)
            res = {
                "data": data.data,
                "meta": {"msg": "获取权限数据成功", "status": 200}
            }
            return JsonResponse(res)
        except Exception as error:
            res = {
                "data": "null",
                "meta": {"msg": "内部错误:{0}".format(error), "status": 500}
            }
            return JsonResponse(res)

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
            res = {
                "data": "null",
                "meta": {"msg": "传入参数错误:{0}".format(format_error(data=data.errors)), "status": 500}
            }
            return JsonResponse(res)
        else:
            data.save()
            data = {
                "data": data.data,
                "meta": {"msg": "权限数据保存成功", "status": 200}
            }
            return JsonResponse(data)


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
            res = {
                "data": "null",
                "meta": {"msg": "查看权限信息失败,PermissionId:{0},原因:不存在".format(permissionId), "status": 500}
            }
            return JsonResponse(res)
        data = PermissionSerializer(instance=query)
        # print(Role.objects.filter(id=roleId))
        res = {
            "data": data.data,
            "meta": {"msg": "查看角色信息成功", "status": 200}
        }
        return JsonResponse(res)

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
            res = {
                "data": "null",
                "meta": {"msg": "修改权限信息失败,PermissionId:{0},原因:不存在".format(permissionId), "status": 500}
            }
            return JsonResponse(res)
        data = PermissionSerializer(instance=query, data=request.data)
        if not data.is_valid():
            res = {
                "data": "null",
                "meta": {"msg": "传入参数错误:{0}".format(format_error(data=data.errors)), "status": 500}
            }
            return JsonResponse(res)
        else:
            data.save()
            res = {
                "data": data.data,
                "meta": {"msg": "修改角色信息成功", "status": 200}
            }
        return JsonResponse(res)

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
            res = {
                "data": "null",
                "meta": {"msg": "权限信息不存在", "status": 500}
            }
            return JsonResponse(res)
        try:
            Permission.objects.get(id=permissionId).delete()
            res = {
                "data": request.data,
                "meta": {"msg": "删除权限成功！", "status": 200}
            }
            return JsonResponse(res)
        except Exception as error:
            res = {
                "data": "null",
                "meta": {"msg": "删除权限失败:{0}".format(error), "status": 500}
            }
            return JsonResponse(res)


class UsersView(APIView):

    def get(self, request):
        """
        :param request:
        :url  /api/v1/user
        :parameter:
        {}
        :return: 查看用户列表
        """
        try:
            query = UserInfo.objects.all()
            data = UserInfoSerializer(instance=query, many=True)
            res = {
                "data": data.data,
                "meta": {"msg": "获取角色成功", "status": 200}
            }
            return JsonResponse(res)
        except Exception as error:
            res = {
                "data": "null",
                "meta": {"msg": "内部错误:{0}".format(error), "status": 500}
            }
            return JsonResponse(res)

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
            res = {
                "data": "null",
                "meta": {"msg": "传入参数错误:{0}".format(format_error(data=data.errors)), "status": 500}
            }
            return JsonResponse(res)
        else:
            data.save()
            user_data = UserInfo.objects.get(username=data.validated_data['username'])
            user_data.set_password("123456")
            user_data.save()
            res = {
                "data": data.data,
                "meta": {"msg": "角色数据保存成功", "status": 200}
            }
            return JsonResponse(res)


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
        except Exception as error:
            res = {
                "data": "null",
                "meta": {"msg": "获取到用户信息失败,UserId:{0},原因:{1}".format(userId, error), "status": 500}
            }
            return JsonResponse(res)
        data = UserInfoSerializer(instance=query)
        res = {
            "data": data.data,
            "meta": {"msg": "获取到用户信息成功", "status": 200}
        }
        return JsonResponse(res)

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
        except Exception as error:
            res = {
                "data": "null",
                "meta": {"msg": "修改用户信息失败,UserId:{0},原因:{1}".format(userId, error), "status": 500}
            }
            return JsonResponse(res)
        data = UserInfoSerializer(instance=query, data=request.data)
        if not data.is_valid():
            res = {
                "data": "null",
                "meta": {"msg": "传入参数错误:{0}".format(format_error(data=data.errors)), "status": 500}
            }
            return JsonResponse(res)
        else:
            data.save()
            res = {
                "data": data.data,
                "meta": {"msg": "修改用户信息成功", "status": 200}
            }
        return JsonResponse(res)

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
            res = {
                "data": request.data,
                "meta": {"msg": "删除信息成功！", "status": 200}
            }
            return JsonResponse(res)
        except Exception as error:
            res = {
                "data": "null",
                "meta": {"msg": "删除角色失败:{0}".format(error), "status": 500}
            }
            return JsonResponse(res)


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
        except Exception as error:
            res = {
                "data": "null",
                "meta": {"msg": "获取到用户密码失败,UserId:{0},原因:{1}".format(userId, error), "status": 500}
            }
            return JsonResponse(res)
        data = ResetPasswordSerializer(user=query, data=request.data)
        if not data.is_valid():
            res = {
                "data": data.data,
                "meta": {"msg": "修改密码失败{0}".format(format_error(data=data.errors)), "status": 500}
            }
            return JsonResponse(res)
        else:
            res = {
                "data": data.data,
                "meta": {"msg": "修改密码成功,用户ID为：{0}".format(userId), "status": 200}
            }
        return JsonResponse(res)


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
        except Exception as error:
            res = {
                "data": "null",
                "meta": {"msg": "修改到用户关联角色失败,UserId:{0},原因:{1}".format(userId, error), "status": 500}
            }
            return JsonResponse(res)
        data = UserEditRoleSerializer(instance=query, data=request.data)
        if not data.is_valid():
            res = {
                "data": "null",
                "meta": {"msg": "修改用户角色失败,{0}".format(format_error(data=data.errors)), "status": 500}
            }
            return JsonResponse(res)
        else:
            data.save()
            res = {
                "data": [],
                "meta": {"msg": "修改密码成功,用户ID为：{0}".format(userId), "status": 200}
            }
            return JsonResponse(res)

    def get(self, request, userId):
        """
        :param request:
        :param userId:
        :return:
        """
        try:
            query = UserInfo.objects.get(id=userId)
        except Exception as error:
            res = {
                "data": "null",
                "meta": {"msg": "修改到用户关联角色失败,UserId:{0},原因:{1}".format(userId, error), "status": 500}
            }
            return JsonResponse(res)
        if not query.roles.exists():
            res = {
                "data": [],
                "meta": {"msg": "获取角色信息成功：{0}".format(userId), "status": 200}
            }
            return JsonResponse(res)
        data = RoleSerializer(instance=query.roles.all(), many=True)
        res = {
            "data": data.data,
            "meta": {"msg": "获取用户角色信息成功，用户id：{0}".format(userId), "status": 200}
        }
        return JsonResponse(res)


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
        except Exception as error:
            res = {
                "data": userId,
                "meta": {"msg": "修改用户状态失败，{0}".format(error), "status": 200}
            }
            return JsonResponse(res)

        data = UserStatusEditSerializer(instance=query, data=request.data)
        if not data.is_valid():
            res = {
                "data": userId,
                "meta": {"msg": "修改用户状态失败,{0}".format(format_error(data=data.errors)), "status": 200}
            }
            return JsonResponse(res)
        else:
            data.save()
            res = {
                "data": userId,
                "meta": {"msg": "修改用户状态成功", "status": 200}
            }
            return JsonResponse(res)

    def get(self, request, userId):
        """
        :param request:
        :param userId:
        :return:
        """
        try:
            query = UserInfo.objects.get(id=userId)
        except Exception as error:
            res = {
                "data": "null",
                "meta": {"msg": "修改到用户关联角色失败,UserId:{0},原因:{1}".format(userId, error), "status": 500}
            }
            return JsonResponse(res)
        res = {
            "data": query.is_active,
            "meta": {"msg": "获取账号状态成功，账号ID：{0}".format(userId), "status": 200}
        }
        return JsonResponse(res)


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
        except Exception as error:
            res = {
                "data": roleId,
                "meta": {"msg": "获取角色信息失败，{0}".format(error), "status": 200}
            }
            return JsonResponse(res)
        data = RolePermissionEditSerializer(instance=query, data=request.data)
        if not data.is_valid():
            res = {
                "data": roleId,
                "meta": {"msg": "修改角色相关权限失败,{0}".format(format_error(data=data.errors)), "status": 200}
            }
            return JsonResponse(res)
        else:
            data.save()
            res = {
                "data": data.data,
                "meta": {"msg": "修改角色权限成功", "status": 200}
            }
            return JsonResponse(res)

    def get(self, request, roleId):
        """
        :param request:
        :param roleId:
        :return:
        """
        try:
            query = Role.objects.get(id=roleId)
        except Exception as error:
            res = {
                "data": roleId,
                "meta": {"msg": "获取角色信息失败，{0}".format(error), "status": 200}
            }
            return JsonResponse(res)

        data = PermissionSerializer(instance=query, many=True)
        res = {
            "data": data.data,
            "meta": {"msg": "获取角色权限成功", "status": 200}
        }
        return JsonResponse(res)


class CurrentUser(APIView):

    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        token_object = UserToken.objects.get(token=token)
        data = UserInfoSerializer(token_object.username)
        # print(data)
        user = ObjectUserInfo()
        menu = data.data
        menu['roles'] = user.get_menu(user_obj=token_object.username)
        print(menu)
        res = {
            "data": menu,
            "meta": {"msg": "获取当前用户信息成功！", "status": 200}
        }
        return JsonResponse(res)


class UserMenu(APIView):

    def get(self, request):
        """
        :param request:
        :return:
        """
        token = request.META.get('HTTP_AUTHORIZATION')
        per = Permission.objects.filter(role__userinfo__usertoken=UserToken.objects.get(token=token))
        data = SubPermissionSerializer(instance=per,many=True)
        # print(data)
        user = ObjectUserInfo()
        user_obj = user.get_user_object(token=token)
        if not user_obj:
            res = {
                "data": [],
                "meta": {"msg": "获取列表失败！", "status": 200}
            }
            return JsonResponse(res)
        menu = user.get_menu(user_obj=user_obj)
        res = {
            "data": menu,
            "meta": {"msg": "获取列表失败！", "status": 200}
        }
        return JsonResponse(res)
