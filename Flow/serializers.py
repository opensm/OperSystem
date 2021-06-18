from rest_framework import serializers
from Flow.models import *
from Task.models import Tasks, FlowTask


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    支持动态指定字段的序列化器，传参fields，序列化和反序列化都支持
    @author: ChenTong
    @Date: 2020.1.26 17:07
    """
    Meta: type

    def __init__(self, *args, **kwargs):
        """支持字段动态生成的序列化器，从默认的Meta.fields中过滤，无关字段不查不序列化"""
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allow = set(fields)
            existing = set(self.fields)
            for f in existing - allow:
                self.fields.pop(f)


class FlowEngineSerializers(serializers.ModelSerializer):
    class Meta:
        model = FlowEngine
        fields = "__all__"


class FlowNodeSerializers(serializers.ModelSerializer):
    class Meta:
        model = FlowNode
        fields = "__all__"


class FlowTaskSerializers(DynamicFieldsModelSerializer):
    task_st = serializers.CharField(source='task.name', read_only=True)
    engine_st = serializers.CharField(source='flow.name', read_only=True)

    class Meta:
        model = FlowTask
        fields = "__all__"

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        Tasks.objects.filter(id=instance.task).update(status='approveing')
        if validated_data['status'] == 'refuse':
            Tasks.objects.filter(id=instance.task).update(status='fail_approve')
        else:
            if not FlowTask.objects.filter(
                    task=instance.task,
                    status__in=['refuse', 'unprocessed']
            ):
                Tasks.objects.filter(id=instance.task).update(status='ok_approved')
        return instance


__all__ = [
    'FlowEngineSerializers',
    'FlowNodeSerializers',
    'FlowTaskSerializers'
]
