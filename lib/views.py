from django.views.generic.base import ContextMixin, TemplateResponseMixin, View
from rest_framework.views import APIView
from lib.mixins import DataQueryPermission
from lib.response import DataResponse


class BaseDetailView(DataQueryPermission, APIView):
    """A base view for displaying a single object."""
    serializer_class = None

    def get(self, request, *args, **kwargs):
        if not self.serializer_class:
            raise TypeError("serializer_class type error!")
        data = self.serializer_class(instance=self.get_user_data_objects(request=request))
        return DataResponse(code="00000", data=data.data, msg="获取数据成功")
