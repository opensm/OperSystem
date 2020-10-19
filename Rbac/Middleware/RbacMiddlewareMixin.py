import re
from django.conf import settings
from django.shortcuts import HttpResponse, render, redirect
from Rbac.models import UserInfo, UserToken, Permission
import datetime
import os


class MiddlewareMixin(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super(MiddlewareMixin, self).__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response


class RbacMiddleware(MiddlewareMixin):

    def format_url(self, obj, path=None):
        """
        :param obj:
        :param path:
        :return:
        """
        # print(obj.path, obj.request_type)
        if not isinstance(obj, Permission):
            raise Exception("输入类型错误！")
        # 当前为页面并没有父页面
        if obj.parent is None and path is None:
            return obj.path
        # 当前为页面并之前也存在页面
        elif obj.parent is None and path is not None:
            return os.path.join(obj.path, path)
        elif obj.parent is not None and path is None:
            return self.format_url(obj=obj.parent, path=obj.path)
        elif obj.parent is not None and path is not None:
            return self.format_url(obj.parent, path=os.path.join(obj.path, path))
        else:
            print(obj.parent, path)

    def process_request(self, request):
        """
        :param request:
        :return:
        """
        # 当前访问的URL
        current_url = request.path_info
        if current_url in ['/api/v1/auth/login']:
            return None
        try:
            token = request.META.get('HTTP_AUTHORIZATION')
        except AttributeError as error:
            return HttpResponse("验证失败,{0}".format(error))
        try:
            token_object = UserToken.objects.get(token=token)
            if token_object.expiration_time < datetime.datetime.now():
                return HttpResponse("验证过期！请重新登陆！")
            permission_list = Permission.objects.filter(
                role__userinfo=token_object.username,
                request_type__isnull=False
            )
        except Exception as error:
            return HttpResponse("权限验证失败,{0}！".format(error))
        flag = 0
        for value in permission_list:
            parch_url = self.format_url(value)
            permission_url = os.path.join('/api/v1', parch_url)
            print(permission_url)
            if re.match(permission_url, current_url) and value.request_type == request.method:
                flag = 1
                continue
        if flag == 0:
            return HttpResponse("没有权限：Error Code 401")

    def process_response(self, request, response):
        return response
