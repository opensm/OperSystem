from rest_framework import serializers
from Task.models import *
from Flow.models import FlowNode
from django.db.models import Max


class AuthKEYSerializers(serializers.ModelSerializer):
    project_st = serializers.CharField(source='project.name', read_only=True)
    create_user_st = serializers.CharField(source='create_user.name', read_only=True)

    class Meta:
        model = AuthKEY
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.user = None
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(AuthKEYSerializers, self).__init__(*args, **kwargs)

    def create(self, validated_data):
        validated_data['create_user'] = self.user
        obj = AuthKEY.objects.create(**validated_data)
        return obj


class TemplateDBSerializers(serializers.ModelSerializer):
    create_user_st = serializers.CharField(source='create_user.name', read_only=True)
    instance_st = serializers.CharField(source='instance.name', read_only=True)
    project_st = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = TemplateDB
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.user = None
        if 'user' in kwargs:
            kwargs.pop('user')
        super(TemplateDBSerializers, self).__init__(*args, **kwargs)

    def create(self, validated_data):
        validated_data['create_user'] = self.user
        obj = TemplateDB.objects.create(**validated_data)
        return obj


class TemplateNacosSerializers(serializers.ModelSerializer):
    create_user_st = serializers.CharField(source='create_user.name', read_only=True)
    instance_st = serializers.CharField(source='auth_key.name', read_only=True)
    project_st = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = TemplateNacos
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.user = None
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(TemplateNacosSerializers, self).__init__(*args, **kwargs)

    def create(self, validated_data):
        validated_data['create_user'] = self.user
        obj = TemplateNacos.objects.create(**validated_data)
        return obj


class TemplateTencentServiceSerializers(serializers.ModelSerializer):
    create_user_st = serializers.CharField(source='create_user.name', read_only=True)
    instance_st = serializers.CharField(source='tencent_key.name', read_only=True)
    project_st = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = TemplateTencentService
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.user = None
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(TemplateTencentServiceSerializers, self).__init__(*args, **kwargs)

    def create(self, validated_data):
        validated_data['create_user'] = self.user
        obj = TemplateTencentService.objects.create(**validated_data)
        return obj


class TemplateKubernetesSerializers(serializers.ModelSerializer):
    create_user_st = serializers.CharField(source='create_user.name', read_only=True)
    instance_st = serializers.CharField(source='cluster.name', read_only=True)
    project_st = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = TemplateKubernetes
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.user = None
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(TemplateKubernetesSerializers, self).__init__(*args, **kwargs)

    def create(self, validated_data):
        validated_data['create_user'] = self.user
        obj = TemplateKubernetes.objects.create(**validated_data)
        return obj


class ExecListSerializers(serializers.ModelSerializer):
    class Meta:
        model = ExecList
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.user = None
        if 'user' in kwargs:
            kwargs.pop('user')
        super(ExecListSerializers, self).__init__(*args, **kwargs)


class SubTaskSerializers(serializers.ModelSerializer):
    exec_list = ExecListSerializers(many=True)
    project_st = serializers.CharField(source='project.name', read_only=True)
    create_user_st = serializers.CharField(source='create_user.name', read_only=True)
    id = serializers.CharField(required=False)

    def __init__(self, *args, **kwargs):
        self.user = None
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(SubTaskSerializers, self).__init__(*args, **kwargs)

    class Meta:
        model = SubTask
        fields = "__all__"

    def validate(self, validated_data):
        """
        :param validated_data:
        :return:
        """
        exec_list = validated_data.pop('exec_list')
        format_list = []
        for data in exec_list:
            object_id = data.get('object_id')
            tmp_model = data.get('content_type').model_class()
            data['content_type'] = data.get('content_type').id
            data['content_object'] = tmp_model.objects.get(id=object_id)
            format_list.append(data)

        data = ExecListSerializers(data=format_list, many=True)
        if not data.is_valid():
            raise serializers.ValidationError('exec_list 字段校验失败！')
        validated_data['exec_list'] = data.save()
        return validated_data

    def update(self, instance, validated_data):
        """
        :param instance:
        :param validated_data:
        :return:
        """
        exec_list = validated_data.pop("exec_list")
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        for many in instance.exec_list.all():
            instance.exec_list.remove(many.id)
        for x in exec_list:
            instance.exec_list.add(x)

        return instance

    def create(self, validated_data):
        """
        :param validated_data:
        :return:
        """
        obj = SubTask.objects.all()
        max_id = obj.aggregate(Max('id'))['id__max']
        if not max_id:
            max_id = 2000001
        else:
            max_id = max_id + 1
        validated_data['id'] = max_id
        exec_list = validated_data.pop('exec_list')
        validated_data['create_user'] = self.user
        obj = SubTask.objects.create(**validated_data)
        obj.save()
        for exe in exec_list:
            obj.exec_list.add(exe)
        return obj


class SubTaskListFields(serializers.RelatedField):
    def to_representation(self, value):
        return '子任务ID: %d,子任务名称：%s ,子任务创建时间:%s' % (value.id, value.container, value.create_time)


class TaskSerializers(serializers.ModelSerializer):
    approval_flow_st = serializers.CharField(source='approval_flow.name', read_only=True)
    project_st = serializers.CharField(source='project.name', read_only=True)
    create_user_st = serializers.CharField(source='create_user.name', read_only=True)
    sub_task_st = SubTaskSerializers(read_only=True, source='sub_task', many=True)

    id = serializers.CharField(required=False)

    class Meta:
        model = Tasks
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.user = None
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(TaskSerializers, self).__init__(*args, **kwargs)

    def create_flow(self, obj, approval_flow):

        data = dict()
        object_list = list()
        for node in FlowNode.objects.filter(flow=approval_flow):
            data['node'] = node
            data['approval_role'] = node.approval_role
            data['level'] = node.level
            data['status'] = ''
            data['task'] = obj
            data['flow'] = approval_flow
            object_list.append(FlowTask(**data))
        FlowTask.objects.bulk_create(objs=object_list)

    def recreate_flow(self, obj, approval_flow):
        FlowTask.objects.filter(task=obj.id).delete()
        self.create_flow(obj=obj, approval_flow=approval_flow)

    def create(self, validated_data):
        """
        :param validated_data:
        :return:
        """
        obj = Tasks.objects.all()
        max_id = obj.aggregate(Max('id'))['id__max']
        if not max_id:
            max_id = 1000001
        else:
            max_id = max_id + 1
        validated_data['id'] = max_id
        sub_task = validated_data.pop('sub_task')
        approval_flow = validated_data['approval_flow']
        validated_data['create_user'] = self.user
        obj = Tasks.objects.create(**validated_data)
        obj.save()
        for exe in sub_task:
            obj.sub_task.add(exe)
            exe.status = 'not_start_exec'
            exe.save()
        self.create_flow(obj=obj, approval_flow=approval_flow)
        return obj

    def update(self, instance, validated_data):
        """
        :param instance:
        :param validated_data:
        :return:
        """
        sub_task = validated_data.pop("sub_task")
        approval_flow = validated_data['approval_flow']
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        for many in instance.sub_task.all():
            instance.sub_task.remove(many)
            many.status = 'unbond'
            many.save()
        for x in sub_task:
            instance.sub_task.add(x)
            x.status = 'not_start_exec'
            x.save()
        self.recreate_flow(obj=instance, approval_flow=approval_flow)
        return instance


class ExecListLogSerializers(serializers.ModelSerializer):
    class Meta:
        model = ExecList
        fields = "__all__"


class ProjectSerializers(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.user = None
        if 'user' in kwargs:
            kwargs.pop('user')
        super(ProjectSerializers, self).__init__(*args, **kwargs)


__all__ = [
    'TaskSerializers',
    'SubTaskSerializers',
    'AuthKEYSerializers',
    'TemplateDBSerializers',
    'TemplateKubernetesSerializers',
    'ExecListLogSerializers',
    'ExecListSerializers',
    'ProjectSerializers',
    'TemplateNacosSerializers',
    'TemplateTencentServiceSerializers'
]
