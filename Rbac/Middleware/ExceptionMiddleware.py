# -*- coding: utf-8 -*-
import json
import logging
import traceback

from django.http import JsonResponse

from .base import BaseReturn

logger = logging.getLogger('root')


class ExceptionBoxMiddleware(object):
    def process_exception(self, request, exception):
        if not issubclass(exception.__class__, BaseReturn):
            return None
        ret_json = {
            'code': exception.__class__.__name__,
            'message': getattr(exception, 'message', ''),
            'result': False,
            'data': ''
        }
        response = JsonResponse(ret_json)
        response.status_code = getattr(exception, 'status_code', 500)
        _logger = logger.error if response.status_code >= 500 else logger.warning
        _logger('status_code->{0}, error_code->{1}, url->{2}, method->{3}, param->{4}, body->{5}，traceback->{6}'.format(
            response.status_code, ret_json['code'], request.path,
            request.method, json.dumps(getattr(request, request.method, {})),
            request.body, traceback.format_exc()
        ))
        return response
