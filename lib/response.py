from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from lib.code import SYSTEM_CODE_DICT


class DataResponse(JsonResponse):
    def __init__(self, data, **kwargs):
        if not isinstance(data, list):
            raise TypeError(
                "返回的数据必须是list类型！"
            )
        if 'code' not in kwargs:
            raise ValueError(
                "必须包含code状态码!"
            )
        code = kwargs.pop('code')
        if kwargs['code'] not in SYSTEM_CODE_DICT:
            params = {
                'data': [],
                'meta': {
                    'msg': SYSTEM_CODE_DICT['50001'],
                    'code': 50001
                }
            }
        else:
            if 'msg' in kwargs:
                msg = kwargs.pop('msg')
            else:
                msg = SYSTEM_CODE_DICT[kwargs['code']]
            params = {
                'data': data,
                'meta': {
                    'msg': msg,
                    'code': kwargs['code']
                }
            }
        if 'token' in kwargs:
            params['token'] = kwargs.pop('token')
        print(params)
        super(DataResponse, self).__init__(data=params, **kwargs)
