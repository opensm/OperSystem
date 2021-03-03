from django.views.generic.base import ContextMixin, TemplateResponseMixin, View
from rest_framework.views import APIView
from lib.mixins import DataQueryPermission
from lib.response import DataResponse
from lib.page import RewritePageNumberPagination


class BaseDetailView(DataQueryPermission, APIView, RewritePageNumberPagination):
    """A base view for displaying a single object."""
    serializer_class = None

    def get(self, request):
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        model_obj = self.get_user_data_objects(request=request)
        page_obj = self.paginate_queryset(queryset=model_obj, request=request, view=self)
        data = self.serializer_class(
            instance=page_obj,
            many=True
        )
        return self.get_paginated_response(
            data=data.data,
            msg="获取数据成功",
            code="00000"
        )


class BaseDeleteView(DataQueryPermission, APIView, RewritePageNumberPagination):
    serializer_class = None

    def delete(self, request):
        model_obj = self.get_user_data_objects(request=request)
        if not model_obj:
            return DataResponse(
                code="00001",
                msg="删除数据异常，获取到删除数据失败！"
            )
        if not self.check_user_permission(model_obj=model_obj, request_type=self.content_type):
            return DataResponse(
                code="00001",
                msg="没有删除权限"
            )
        else:
            return DataResponse(
                code="00000",
                msg="删除信息成功!"
            )

    def put(self, request):
        """
        :param request:
        :return:
        """
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        model_objs = self.get_user_data_objects(request=request)
        data = self.serializer_class(
            instance=model_objs,
            many=True,
            data=request.data
        )

        if not data.is_valid():
            return DataResponse(data=request.data, msg="数据输入格式不匹配", code="00001")
        try:
            data.save()
            return DataResponse(msg="数据保存成功", code="00000")
        except Exception as error:
            return DataResponse(
                data=request.data,
                msg="数据保存失败:%s" % error,
                code="00001"
            )

    def get(self, request):
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        model_obj = self.get_user_data_objects(request=request)
        page_obj = self.paginate_queryset(queryset=model_obj, request=request, view=self)
        data = self.serializer_class(
            instance=page_obj,
            many=True
        )
        return self.get_paginated_response(
            data=data.data,
            msg="获取数据成功",
            code="00000"
        )
