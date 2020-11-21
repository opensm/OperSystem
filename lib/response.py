from django.http import JsonResponse
from lib.code import SYSTEM_CODE_DICT


class DataResponse(JsonResponse):
    def __init__(self, data=None, **kwargs):
        if data is None:
            data = []
        if not isinstance(data, (list, dict)):
            raise TypeError(
                "返回的数据必须是list,或者dict类型！"
            )
        if 'code' not in kwargs:
            raise ValueError(
                "必须包含code状态码!"
            )
        code = kwargs.pop('code')
        if not isinstance(code, str):
            raise TypeError(
                'code类型错误，必须是str类型!'
            )
        if code not in SYSTEM_CODE_DICT:
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
                msg = SYSTEM_CODE_DICT[code]
            params = {
                'data': data,
                'meta': {
                    'msg': msg,
                    'code': code
                }
            }
        if 'token' in kwargs:
            params['token'] = kwargs.pop('token')
        super(DataResponse, self).__init__(data=params, **kwargs)
