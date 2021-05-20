from collections import OrderedDict
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
from copy import deepcopy


# 自定义分页类
class RewritePageNumberPagination(PageNumberPagination):
    # 每页显示多少个
    page_size = 10
    # 默认每页显示3个，可以通过传入pager1/?page=2&size=4,改变默认每页显示的个数
    page_size_query_param = "size"
    # 最大页数不超过10
    max_page_size = 1000
    # 获取页码数的
    page_query_param = "page"
    sort_query_param = "sort"

    def get_paginated_response(self, data, msg=None, post=False, code="00000"):
        """
        :param data:
        :param msg:
        :param post:
        :param code:
        :return:
        """
        if msg is None:
            raise ValueError("msg不能为空")
        if not isinstance(code, str):
            raise TypeError('code 类型错误，必须是string')
        meta = {'msg': msg, 'code': code, 'post_tag': post}
        return Response(OrderedDict([
            ('total', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('data', data),
            ('meta', meta),
            ('pagesize', self.page.has_other_pages())
        ]))

    def paginate_queryset(self, queryset, request, view=None):
        """
        :param queryset:
        :param request:
        :param view:
        :return:
        """
        models_queryset = deepcopy(queryset[0])
        params = dict()
        for field in models_queryset._meta.fields:
            for key, value in request.query_params.items():
                if field.name != key:
                    continue
                if type(field).__name__ in ['CharField', 'Textfield']:
                    params["{0}__contains".format(key)] = value
                else:
                    params[key] = value
        queryset = queryset.filter(**params)
        sort_by = request.query_params.get(self.sort_query_param, '+id').strip('+')
        if not hasattr(queryset, sort_by.strip('-')) and sort_by.strip('-') != 'id':
            raise ValueError(
                '不包含字段:{0}'.format(sort_by)
            )
        return super(RewritePageNumberPagination, self).paginate_queryset(
            queryset=queryset.order_by(sort_by),
            request=request,
            view=view
        )


class LimitRewritePageNumberPagination(LimitOffsetPagination):
    default_limit = 5  # 前台不传每页默认显示条数

    limit_query_param = 'page'  # 前天控制每页的显示条数查询参数，一般不需要改，系统默认为 limit 变量
    offset_query_param = 'offset'  # 前天控制从哪一条开始显示的查询参数
    # eg:http://127.0.0.1: 8122/book/?xx=5&offset=7  表示显示第8条开始，往下显示5条记录
    max_limit = 10  # 后台控制显示的最大条数防止前台输入数据过大

    def get_paginated_response(self, data, msg=None, code="00000"):
        """
        :param data:
        :param msg:
        :param code:
        :return:
        """
        if msg is None:
            raise ValueError("msg不能为空")
        if not isinstance(code, str):
            raise TypeError('code 类型错误，必须是string')
        meta = {'msg': msg, 'code': code}
        return Response(OrderedDict([
            ('total', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('data', data),
            ('meta', meta)
        ]))


__all__ = ['RewritePageNumberPagination', 'LimitRewritePageNumberPagination']
