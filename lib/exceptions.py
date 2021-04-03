from django.utils.translation import gettext_lazy as _
from lib.code.status import *


class APIException(Exception):
    """
    Base class for REST framework exceptions.
    Subclasses should provide `.status_code` and `.default_detail` properties.
    """
    status_code = API_50001_SERVER_ERROR
    default_detail = _('A server error occurred.')
    default_code = 'error'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        print(code)
        print(detail)

        # self.detail = _get_error_details(detail, code)

    # def __str__(self):
    #     return str(self.detail)
