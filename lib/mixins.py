from django.apps import apps as django_apps
from django.db.models import query
from django.db.models import Q
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
    error_message = {}
    kwargs = None

    def __init__(self):
        ObjectUserInfo.__init__(self)
        self.user = None
        self.__object = None
        self.__model = django_apps.get_model(
            "{0}.{1}".format(
                self.app_label, self.model_name
            )
        )

    def get_user_data_permission(self):
        """
        :return:
        """
        model = django_apps.get_model("Rbac.DataPermissionList")
        if not self.user.usertoken.expiration_time > datetime.datetime.now() or not self.user.is_active:
            return []
        permission_list = list()
        for role in self.user.roles.all():
            for content in role.data_permission.filter(content_type=self.__model):
                permission = model.objects.get(
                    permission_rule=content,
                )
                if not permission:
                    continue
                permission_list.append((
                    content.content_type,
                    permission,
                    content.request_type
                ))
        return permission_list

    def get_user_model_data_permission(self):
        """
        :return:
        """
        if not isinstance(self.model_name, str):
            return []
        if not self.__model:
            raise ValueError("french model value error!")
        # 超级管理员直接返回结果
        if self.user.is_superuser and self.user.is_active:
            self.__object = self.__model.objects.all()
            return self.__object
        # 用户状态为不生效，返回空
        elif not self.user.is_active:
            return self.__object
        for data in self.get_user_data_permission():
            self.get_permission_rule_q(data=data)

    def get_permission_rule_q(self, data):
        """
        :param data:
        :return:
        """
        params = dict()
        if not isinstance(data, tuple):
            raise TypeError("输入参数必须为元组:{0}，请检查".format(data))
        query_set = data[1]
        if len(query_set):
            return []
        content = data[0]
        for x in query_set:
            params.setdefault(
                x.check_field,
                []
            ).append({
                'operate': x.operate_choice,
                'value': x.value
            })
        a = Q()
        for key, value in params.items():
            a_t = Q()
            a_t.connector = 'OR'
            for v in value:
                a_t.children.append((key, v))
            a.add(a_t, 'ADD')
        return (
            content.objects.filter(a),
            data[2]
        )

    def get_model_fields(self):
        field_name = dict()
        if not self.__model:
            raise ValueError("请先输入model参数实例化相关数据！")
        for x in self.__model._meta.fields:
            field_name[x.name] = x.verbose_name
        return field_name

    def get_field_values(self, field):
        """
        :param field:
        :return:
        """
        if not self.__object:
            raise ValueError("请先通过 get_user_model_data_permission实例化相关数据！")
        fields = self.get_model_fields()
        if field not in fields.keys():
            return []
        return list(set([getattr(x, field) for x in self.__object]))

    def check_user_permission(self, model_obj, request_type='POST'):
        """
        :param model_obj:
        :param request_type:
        :return:
        """
        for data in self.get_user_data_permission():
            params = {data.check_field: data.value}
            model_check = data.content_type.filter(**params)
            method = [x.method for x in data.content_type.all()]
            if model_obj in model_check and request_type in method:
                return True
        return False

    def check_user_permissions(self, model_objects, request_method):
        """
        :param model_objects:
        :param request_method:
        :return:
        """
        errors = list()
        print(model_objects)
        print(type(model_objects))
        for s in model_objects:
            if not self.check_user_permission(model_obj=s, request_type=request_method):
                errors.append("ID:{0},权限不存在!".format(s.id))
        if errors:
            self.error_message = ','.join(list(set(errors))).rstrip(',')
        if self.error_message:
            return False
        else:
            return True

    def get_request_filter(self, request):
        """
        :param request:
        :return:
        """
        filter_dict = dict()
        kwargs = getattr(request, request.method)
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
        if len(filter_dict) != 0:
            self.kwargs = filter_dict

    def get_user_data_objects(self, request):
        """
        :return:
        """
        self.user = self.get_user_object(request=request)
        self.get_user_model_data_permission()
        if not self.__object:
            return self.__object
        elif self.kwargs:
            return self.__object.filter(**self.kwargs)
        else:
            return self.__object
