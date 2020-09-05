# -*- coding: utf-8 -*-
from rest_framework.views import APIView
from Rbac.models import *
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
        return JsonResponse(request.data)

    def get(self, request):
        print(request.data)
        return JsonResponse(request.data)
