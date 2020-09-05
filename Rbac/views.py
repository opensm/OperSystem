# -*- coding: utf-8 -*-
from rest_framework.views import APIView
from Rbac.models import *
import hashlib
import datetime
from django.contrib import auth
from django.http import JsonResponse


class AuthView(APIView):
    def post(self, request):
        res = dict()
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
                token = hashlib.md5(username)
                # 保存(存在就更新不存在就创建，并设置过期时间为5分钟)
                expiration_time = datetime.datetime.now() + datetime.timedelta(minutes=60)
                print(expiration_time, type(expiration_time))
                defaults = {
                    "token": token,
                    "expiration_time": expiration_time
                }
                UserToken.objects.update_or_create(user=user_obj, defaults=defaults)
                return JsonResponse({"code": 200, "token": token})
            else:
                return JsonResponse({"code": 401, "error": "用户名或密码错误"})
        except Exception as e:
            print(e)
            return JsonResponse({"code": 500, "error": "用户名或密码错误"})

    def get(self, request):
        print(request.data)
        return JsonResponse(request.data)
