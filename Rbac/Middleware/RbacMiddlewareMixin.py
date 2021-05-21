from Rbac.models import UserToken
from lib.response import DataResponse
from django.urls import resolve
import datetime

RESPONSE_STATUS = {
    'TOKEN_NOT_EXIST': "Token值不存在，请校验上传参数！",
    'TOKEN_EXPIRATION': "Token已超时，请重新登录！",
    'TOKEN_ERROR_AUTH': "Token校验异常，请重试！",
    'TOKEN_SUCCESS_AUTH': "Token校验成功！"
}


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


def check_token(request):
    if 'HTTP_AUTHORIZATION' not in request.META:
        return 'TOKEN_NOT_EXIST'
    token = request.META.get('HTTP_AUTHORIZATION')
    try:
        token_object = UserToken.objects.get(token=token)
    except UserToken.DoesNotExist:
        return 'TOKEN_ERROR_AUTH'

    if token_object.expiration_time < datetime.datetime.now():
        return 'TOKEN_EXPIRATION'
    else:
        return 'TOKEN_SUCCESS_AUTH'


class RbacMiddleware(MiddlewareMixin):

    def process_request(self, request):
        """
        :param request:
        :return:
        """
        # 当前访问的URL
        resolve_url_obj = resolve(request.path_info)
        if resolve_url_obj.url_name in ['login']:
            return None
        token_status = check_token(request=request)
        if token_status != 'TOKEN_SUCCESS_AUTH':
            return DataResponse(msg=RESPONSE_STATUS[token_status], code='00001')
        flag = 1

        if flag == 0:
            return DataResponse(msg="没有权限：Error Code 401", code='00001')

    def process_response(self, request, response):
        return response
