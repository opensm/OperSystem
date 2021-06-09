from rest_framework import serializers
from Task.models import *
from lib.Log import RecodeLog
from django.contrib.contenttypes.models import ContentType
from Flow.models import FlowTask, FlowEngine, FlowNode
from Flow.serializers import FlowTaskSerializers


class AuthKEYSerializers(serializers.ModelSerializer):
    class Meta:
        model = AuthKEY
        fields = ("__all__")


class TaskSerializers(serializers.ModelSerializer):
    class Meta:
        model = Tasks
        fields = ("__all__")

    def create_flow(self, obj, approval_flow):

        data = dict()
        object_list = list()
        for node in FlowNode.objects.filter(flow=approval_flow):
            data['node'] = node
            data['approval_role'] = node.approval_role
            data['level'] = node.level
            data['status'] = 'unprocessed'
            data['task'] = obj.pk
            data['flow'] = approval_flow
            object_list.append(FlowTask(**data))
        objs = FlowTask.objects.bulk_create(objs=object_list)
        # objs.save()

    def recreate_flow(self, obj, approval_flow):
        FlowTask.objects.filter(task=obj.id).delete()
        self.create_flow(obj=obj, approval_flow=approval_flow)

    def create(self, validated_data):
        """
        :param validated_data:
        :return:
        """
        sub_task = validated_data.pop('sub_task')
        approval_flow = validated_data['approval_flow']
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


class TemplateDBSerializers(serializers.ModelSerializer):
    class Meta:
        model = TemplateDB
        fields = "__all__"


class TemplateNacosSerializers(serializers.ModelSerializer):
    class Meta:
        model = TemplateNacos
        fields = "__all__"


class TemplateTencentServiceSerializers(serializers.ModelSerializer):
    class Meta:
        model = TemplateTencentService
        fields = "__all__"


class TemplateKubernetesSerializers(serializers.ModelSerializer):
    class Meta:
        model = TemplateKubernetes
        fields = "__all__"


class ExecListSerializers(serializers.ModelSerializer):
    class Meta:
        model = ExecList
        fields = "__all__"


class SubTaskserializers(serializers.ModelSerializer):
    exec_list = ExecListSerializers(many=True)

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
        exec_list = validated_data.pop('exec_list')
        obj = SubTask.objects.create(**validated_data)
        obj.save()
        for exe in exec_list:
            obj.exec_list.add(exe)
        return obj


class ExecListLogSerializers(serializers.ModelSerializer):
    class Meta:
        model = ExecList
        fields = "__all__"


class ProjectSerializers(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


__all__ = [
    'TaskSerializers',
    'SubTaskserializers',
    'AuthKEYSerializers',
    'TemplateDBSerializers',
    'TemplateKubernetesSerializers',
    'ExecListLogSerializers',
    'ExecListSerializers',
    'ProjectSerializers',
    'TemplateNacosSerializers',
    'TemplateTencentServiceSerializers'
]
