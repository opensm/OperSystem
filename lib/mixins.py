from django.apps import apps as django_apps
from KubernetesManagerWeb.settings import AUTH_USER_MODEL
import datetime


class ObjectUserInfo:
    def __init__(self):
        self.user_object_type = django_apps.get_model(AUTH_USER_MODEL)
        self.token = None
        self.button_code = 999

    @property
    def get_user_model(self):
        return django_apps.get_model(AUTH_USER_MODEL)

    def get_user_object(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        user = self.get_user_model
        try:
            return user.objects.get(usertoken__token=token)
        except user.DoesNotExist:
            return None


class DataQueryPermission(ObjectUserInfo):
    model_name = None
    app_label = None
    content_type = None
    error_message = {}

    def __init__(self):
        ObjectUserInfo.__init__(self)
        self.user = None
        self.__object = None
        self.__model = None
        # self.model_name = None
        # self.app_label = None
        # self.content_type = None

    def get_user_data_permission(self):
        """
        :return:
        """
        model = django_apps.get_model("Rbac.DataPermissionList")
        if not self.user.usertoken.expiration_time > datetime.datetime.now() or not self.user.is_active:
            return []
        return [data for data in model.objects.filter(
            role__in=self.user.roles.all()
        )]

    def get_user_model_data_permission(self):
        """
        :return:
        """
        if not isinstance(self.model_name, str):
            return []
        params = dict()
        if not self.__model:
            self.__model = django_apps.get_model("{0}.{1}".format(
                self.app_label, self.model_name
            ))
        # 超级管理员直接返回结果
        if self.user.is_superuser and self.user.is_active:
            self.__object = self.__model.objects.all()
            return self.__object
        # 用户状态为不生效，返回空
        elif not self.user.is_active:
            return self.__object
        for data in self.get_user_data_permission():
            if data.content_type != self.__model:
                continue
            try:
                value = int(data.value)
            except TypeError:
                value = data.value
            params.setdefault(data.check_field, []).append(value)
        filter_dict = dict()
        for key, value in params.items():
            if len(value) == 0:
                continue
            elif len(value) == 1:
                filter_dict = {key: value}
            else:
                filter_dict = {"{0}__in".format(key): value}
        self.__object = self.__model.objects.filter(**filter_dict)
        return self.__object

    def get_model_fields(self):
        if not self.__object:
            return []
        if not self.__model:
            raise ValueError("请先通过 get_user_model_data_permission实例化相关数据！")
        return [x.name for x in self.__model._meta.fields]

    def get_field_values(self, field):
        """
        :param field:
        :return:
        """
        if not self.__object:
            raise ValueError("请先通过 get_user_model_data_permission实例化相关数据！")
        fields = self.get_model_fields()
        if field not in fields:
            return []
        return list(set([getattr(x, field) for x in self.__object]))

    def check_user_permission(self, model_obj, request_type='POST'):
        """
        :param model_obj:
        :param request_type:
        :return:
        """
        check_status = False
        data_permission = self.get_user_data_permission()
        for data in data_permission:
            if model_obj != data:
                continue
            if data.request_type.filter(method=request_type):
                check_status = True
                break
        return check_status

    def get_request_filter(self, request):
        """
        :param request:
        :return:
        """
        filter_dict = dict()
        kwargs = getattr(request, self.content_type)
        fields = self.get_model_fields()

        for key, value in kwargs.items():
            if key not in fields:
                continue
            if len(value) == 0:
                continue
            elif len(value) == 1:
                filter_dict = {key: value[0]}
            else:
                filter_dict = {"{0}__in".format(key): value}
        if len(filter_dict) == 0:
            return self.__object
        return self.__object.filter(**filter_dict)

    def get_user_data_objects(self, request):
        """
        :return:
        """
        self.user = self.get_user_object(request=request)
        self.get_user_model_data_permission()
        return self.get_request_filter(request=request)
