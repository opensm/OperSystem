# -*- coding: utf-8 -*-
from rest_framework.views import APIView
from Rbac.models import *
from django.http import JsonResponse
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
    UserEditRoleSerializer


class AuthView(APIView):
    def post(self, request):
        signin = SignInSerializer(data=request.data)
        if not signin.is_valid():
            error_message = ""
            for key, value in signin.errors.items():
                if key == "non_field_errors":
                    error_message = "{0};{1}".format(error_message, ",".join(value))
                else:
                    error_message = "{0}{1}：{2}".format(error_message, key, ",".join(value))
            res = {
                "data": "null",
                "meta": {"msg": error_message.lstrip(';'), "status": 401}
            }
            return JsonResponse(res)
        md5 = hashlib.md5(
            "{0}{1}{2}".format(signin.username, time.time(), SECRET_KEY).encode("utf8")
        )
        token = md5.hexdigest()
        # 保存(存在就更新不存在就创建，并设置过期时间为60分钟)
        expiration_time = datetime.datetime.now() + datetime.timedelta(minutes=60)
        defaults = {
            "token": token,
            "expiration_time": expiration_time,
            "update_date": datetime.datetime.now()
        }
        try:
            UserToken.objects.update_or_create(username=signin.username, defaults=defaults)
            return {
                "data": "null",
                "token": token,
                "meta": {"msg": "登录成功！", "status": 200}
            }
        except Exception as error:
            return {
                "data": "null",
                "meta": {"msg": "登录失败，用户token更新失败，{0}".format(error), "status": 500}
            }


class RolesView(APIView):

    def get(self, request):
        try:
            data = Role.objects.all()
            ret = RoleSerializer(instance=data, many=True)
            res = {
                "data": ret.data,
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
        res = RoleSerializer(data=request.data)
        if not res.is_valid():
            res = {
                "data": "null",
                "meta": {"msg": "传入参数错误:{0}".format(res.errors), "status": 500}
            }
            return JsonResponse(res)
        else:
            res.save()
            data = {
                "data": res.data,
                "meta": {"msg": "角色数据保存成功", "status": 200}
            }
            return JsonResponse(data)


class RoleView(APIView):

    def get(self, request, roleId):
        """
        :param request:
        :param roleId:
        :return: 查看具体角色信息
        """
        ret = RoleSerializer(Role.objects.filter(id=roleId).first())
        # print(Role.objects.filter(id=roleId))
        data = {
            "data": ret.data,
            "meta": {"msg": "查看角色信息成功", "status": 200}
        }
        return JsonResponse(data)

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
        :return: 修改角色信息
        """
        query = Role.objects.filter(pk=roleId).first()
        ret = RoleSerializer(instance=query, data=request.data)
        if not ret.is_valid():
            res = {
                "data": "null",
                "meta": {"msg": "传入参数错误:{0}".format(ret.errors), "status": 500}
            }
            return JsonResponse(res)
        else:
            ret.update(instance=query, validated_data=ret.validated_data)
            # result = serializers.serialize('json', data)
            res = {
                "data": ret.data,
                "meta": {"msg": "修改角色信息成功", "status": 200}
            }
        return JsonResponse(res)

    def delete(self, request, roleId):
        """
        :param request:
        :param roleId:
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
        :return:
        """
        try:
            data = Permission.objects.all()
            ret = PermissionSerializer(instance=data, many=True)
            res = {
                "data": ret.data,
                "meta": {"msg": "获取权限数据成功", "status": 200}
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
        :return:
        """
        res = PermissionSerializer(data=request.data)
        if not res.is_valid():
            res = {
                "data": "null",
                "meta": {"msg": "传入参数错误:{0}".format(res.errors), "status": 500}
            }
            return JsonResponse(res)
        else:
            res.save()
            data = {
                "data": res.data,
                "meta": {"msg": "权限数据保存成功", "status": 200}
            }
            return JsonResponse(data)


class PermissionView(APIView):

    def get(self, request, permissionId):
        """
        :param request:
        :param permissionId:
        :return: 查看具体角色信息
        """
        ret = PermissionSerializer(Permission.objects.filter(id=permissionId).first())
        # print(Role.objects.filter(id=roleId))
        data = {
            "data": ret.data,
            "meta": {"msg": "查看角色信息成功", "status": 200}
        }
        return JsonResponse(data)

    def put(self, request, permissionId):
        """
        :param request:
        :param permissionId:
        :return: 修改角色信息
        """
        if not Permission.objects.filter(id=permissionId).exists():
            res = {
                "data": "null",
                "meta": {"msg": "权限信息不存在", "status": 500}
            }
            return JsonResponse(res)
        query = Permission.objects.filter(pk=permissionId).first()
        ret = PermissionSerializer(instance=query, data=request.data)
        if not ret.is_valid():
            res = {
                "data": "null",
                "meta": {"msg": "传入参数错误:{0}".format(ret.errors), "status": 500}
            }
            return JsonResponse(res)
        else:
            ret.update(instance=query, validated_data=ret.validated_data)
            res = {
                "data": ret.data,
                "meta": {"msg": "修改角色信息成功", "status": 200}
            }
        return JsonResponse(res)

    def delete(self, request, permissionId):
        """
        :param request:
        :param permissionId:
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
        try:
            data = UserInfo.objects.all()
            ret = UserInfoSerializer(instance=data, many=True)
            res = {
                "data": ret.data,
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
        res = UserInfoSerializer(data=request.data)
        if not res.is_valid():
            res = {
                "data": "null",
                "meta": {"msg": "传入参数错误:{0}".format(res.errors), "status": 500}
            }
            return JsonResponse(res)
        else:
            res.save()
            data = {
                "data": res.data,
                "meta": {"msg": "角色数据保存成功", "status": 200}
            }
            return JsonResponse(data)


class UserView(APIView):

    def get(self, request, userId):
        """
        :param request:
        :param userId:
        :return: 查看具体角色信息
        """
        ret = UserInfoSerializer(UserInfo.objects.filter(id=userId).first())
        # print(Role.objects.filter(id=roleId))
        data = {
            "data": ret.data,
            "meta": {"msg": "查看角色信息成功", "status": 200}
        }
        return JsonResponse(data)

    def post(self, request):
        """
        :param request:
        :return:修改角色权限分配
        """
        return JsonResponse({"data": "post"})

    def put(self, request, userId):
        """
        :param request:
        :param userId:
        :return: 修改角色信息
        """
        query = UserInfo.objects.filter(pk=userId).first()
        ret = UserInfoSerializer(instance=query, data=request.data)
        if not ret.is_valid():
            res = {
                "data": "null",
                "meta": {"msg": "传入参数错误:{0}".format(ret.errors), "status": 500}
            }
            return JsonResponse(res)
        else:
            ret.update(instance=query, validated_data=ret.validated_data)
            # result = serializers.serialize('json', data)
            res = {
                "data": ret.data,
                "meta": {"msg": "修改用户信息成功", "status": 200}
            }
        return JsonResponse(res)

    def delete(self, request, userId):
        """
        :param request:
        :param userId:
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
        :return:
        """
        query = UserInfo.objects.get(id=userId)
        reset_ser = ResetPasswordSerializer(user=query, data=request.data)
        if not reset_ser.is_valid():
            res = {
                "data": "null",
                "meta": {"msg": "修改失败{0}".format(reset_ser.errors), "status": 500}
            }
            return JsonResponse(res)
        else:
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
        res = {
            "data": userId,
            "meta": {"msg": "修改用户信息成功", "status": 200}
        }
        return JsonResponse(res)


class UserEditRoleView(APIView):

    def put(self, request, userId):
        """
        :param request:
        :param userId:
        :return:
        """
        query = UserInfo.objects.get(id=userId)
        data = UserEditRoleSerializer(instance=query, data=request.data)
        if not data.is_valid():
            return {
                "data": "null",
                "meta": {"msg": "修改失败{0}".format(data.errors), "status": 500}
            }
        else:
            data.save()
            return {
                "data": [],
                "meta": {"msg": "修改密码成功,用户ID为：{0}".format(userId), "status": 200}
            }
