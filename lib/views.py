from django.views.generic.base import ContextMixin, TemplateResponseMixin, View
from rest_framework.views import APIView
from lib.mixins import DataQueryPermission
from lib.response import DataResponse
from lib.page import RewritePageNumberPagination


class BaseListView(DataQueryPermission, APIView, RewritePageNumberPagination):
    """A base view for displaying a single object."""
    serializer_class = None

    def get_user_data_objects(self, request):
        if self.page_size_query_param in self.kwargs:
            self.kwargs.pop(self.page_size_query_param)
        if self.page_query_param in self.kwargs:
            self.kwargs.pop(self.page_query_param)
        if self.sort_query_param in self.kwargs:
            self.kwargs.pop(self.sort_query_param)
        return super().get_user_data_objects(request)

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


class BaseDetailView(DataQueryPermission, APIView, RewritePageNumberPagination):
    serializer_class = None
    pk = None

    def get_user_data_objects(self, request):
        if self.page_size_query_param in self.kwargs:
            self.kwargs.pop(self.page_size_query_param)
        if self.page_query_param in self.kwargs:
            self.kwargs.pop(self.page_query_param)
        if self.sort_query_param in self.kwargs:
            self.kwargs.pop(self.sort_query_param)
        return super().get_user_data_objects(request)

    def delete(self, request):
        model_obj = self.get_user_data_objects(request=request)
        if not model_obj:
            return DataResponse(
                code="00001",
                msg="删除数据异常，获取到删除数据失败！"
            )
        if not self.check_user_permissions(
                model_objects=model_obj, request_method=request.method
        ):
            return DataResponse(
                code="00001",
                msg=self.error_message
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
        if not self.check_user_permissions(model_objects=model_objs, request_method=request.method):
            return DataResponse(
                code="00001",
                msg=self.error_message
            )
        if not data.is_valid():
            return DataResponse(data=request.data, msg="数据输入格式不匹配:{0}".format(data.errors), code="00001")
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
