import re
from django.conf import settings
from django.shortcuts import HttpResponse, render, redirect
from Rbac.models import UserInfo, UserToken, Permission
import datetime


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

    def process_request(self, request):
        """
        :param request:
        :return:
        """
        # 当前访问的URL
        try:
            token = request.META.get('HTTP_AUTHORIZATION')
        except AttributeError as error:
            print(error)
            return False
        current_url = request.path_info
        try:
            token_object = UserToken.objects.get(token=token)
            if token_object.expiration_time < datetime.datetime.now():
                return HttpResponse("验证过期！请重新登陆！")
            permission_list = Permission.objects.filter(role__userinfo=token_object.username)
        except Exception as error:
            print(error)
            return HttpResponse("权限验证失败！")

        for value in permission_list:
            print(current_url)
            print(value.path)
        # # 当前用户的所有权限
        # permission_dict = request.session.get(settings.PERMISSION_DICT_SESSION_KEY)
        # if permission_dict is None:
        #     return HttpResponse("没有权限！")

        # 用户权限和当前URL进行匹配
        flag = False
        for item in permission_dict.values():

            urls = item['urls']
            codes = item['codes']
            for rex in urls:
                reg = settings.REX_FORMAT % (rex,)
                if re.match(reg, current_url):
                    flag = True
                    request.permission_codes = codes
                    break
            if flag:
                break
        if not flag:
            return render(request, "404.html")

    def process_response(self, request, response):
        return response
