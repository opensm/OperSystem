from Flow.serializers import *
from lib.views_v2 import *


class FlowEnginesView(BaseListView):
    serializer_class = FlowEngineSerializers
    model_name = 'FlowEngine'
    app_label = 'Flow'
    page_size_query_param = 'limit'
    sort_query_param = 'sort'


class FlowEngineView(BaseDetailView):
    serializer_class = FlowEngineSerializers
    model_name = 'FlowEngine'
    app_label = 'Flow'
    pk = 'id'


class FlowNodesView(BaseListView):
    serializer_class = FlowNodeSerializers
    model_name = 'FlowNode'
    app_label = 'Flow'
    page_size_query_param = 'limit'
    sort_query_param = 'sort'


class FlowNodeView(BaseDetailView):
    serializer_class = FlowNodeSerializers
    model_name = 'FlowNode'
    app_label = 'Flow'
    pk = 'id'


class FlowTaskView(BaseFlowPUTVIEW):
    serializer_class = FlowTaskSerializers
    model_name = 'FlowTask'
    app_label = 'Flow'
    pk = 'id'
    fields = ['status']


class FlowTasksView(BaseFlowGETVIEW):
    serializer_class = FlowTaskSerializers
    model_name = 'FlowTask'
    app_label = 'Task'
    page_size_query_param = 'limit'
    sort_query_param = 'sort'


__all__ = [
    'FlowNodeView',
    'FlowNodesView',
    'FlowEngineView',
    'FlowEnginesView',
    'FlowTaskView',
    'FlowTasksView'
]
