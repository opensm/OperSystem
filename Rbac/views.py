# -*- coding: utf-8 -*-
from rest_framework.views import APIView
from Rbac.models import *
from KubernetesManagerWeb.settings import SECRET_KEY
import hashlib
import datetime, time
from django.contrib import auth
from django.http import JsonResponse
from django.core import serializers
from serializers import RoleSerializer


class AuthView(APIView):
    def post(self, request):
        if 'username' not in request.data or 'password' not in request.data:
            res = {
                "data": "null",
                "meta": {"msg": "请求格式异常", "status": 401}
            }
            return JsonResponse(res)
        try:
            username = request.data["username"]
            password = request.data["password"]
            user_obj = auth.authenticate(username=username, password=password)
            if user_obj:
                # 为登录用户创建token
                md5 = hashlib.md5("{0}{1}{2}".format(username, time.time(), SECRET_KEY).encode("utf8"))
                token = md5.hexdigest()
                # 保存(存在就更新不存在就创建，并设置过期时间为5分钟)
                expiration_time = datetime.datetime.now() + datetime.timedelta(minutes=60)
                defaults = {
                    "token": token,
                    "expiration_time": expiration_time,
                    "update_date": datetime.datetime.now()
                }
                UserToken.objects.update_or_create(username=user_obj, defaults=defaults)
                res = {
                    "data": "null",
                    "token": token,
                    "meta": {"msg": "登录成功", "status": 200}
                }
                return JsonResponse(res)
            else:
                res = {
                    "data": "null",
                    "token": "null",
                    "meta": {"msg": "请求格式异常", "status": 401}
                }
                return JsonResponse(res)
        except Exception as e:
            res = {
                "data": "null",
                "token": "null",
                "meta": {"msg": "内部错误:{0}".format(e), "status": 500}
            }
            return JsonResponse(res)

    def get(self, request):
        print(request.data)
        return JsonResponse(request.data)


class RolesView(APIView):
    def get(self, request):
        try:
            data = serializers.serialize('json', Role.objects.all())
            # data = Role.objects.all()
            res = {
                "data": data,
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
                "meta": {"msg": "传入参数错误:{0}".format(res.errors), "status": 300}
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

    def get(self, request):
        """
        :param request:
        :return:
        """
        return JsonResponse({"data": "get"})

    def post(self, request):
        return JsonResponse({"data": "post"})

    def put(self, request):
        return JsonResponse({"data": "put"})

    def delete(self, request):
        return JsonResponse({"data": "delete"})
