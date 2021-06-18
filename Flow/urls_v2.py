from django.urls import path
from Flow.views_v2 import *

urlpatterns = [
    # 用户登录
    path('flow_node', FlowNodeView.as_view(), name='flow_node'),
    path('flow_nodes', FlowNodesView.as_view(), name='flow_nodes'),
    path('flow_engine', FlowEngineView.as_view(), name='flow_engine'),
    path('flow_engines', FlowEnginesView.as_view(), name='flow_engines'),
    path('flow_task', FlowTaskView.as_view(), name='flow_task'),
    path('flow_tasks', FlowTasksView.as_view(), name='flow_task')
]
