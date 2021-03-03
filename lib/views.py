from django.views.generic.base import ContextMixin, TemplateResponseMixin, View
from rest_framework.views import APIView
from lib.mixins import DataQueryPermission
from lib.response import DataResponse
from lib.page import RewritePageNumberPagination


class BaseDetailView(DataQueryPermission, APIView, RewritePageNumberPagination):
    """A base view for displaying a single object."""
    serializer_class = None

    def get(self, request, *args, **kwargs):
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        model_obj = self.get_user_data_objects(request=request)
        page_obj = self.paginate_queryset(queryset=model_obj, request=request, view=self)
        print(page_obj)
        data = self.serializer_class(
            instance=page_obj,
            many=True
        )
        return self.get_paginated_response(
            data=data,
            msg="获取数据成功",
            code=00000
        )
        # return DataResponse(code="00000", data=data.data, msg="获取数据成功")
