from django.urls import path, re_path
from Task.views_v2 import *

urlpatterns = [
    # 用户登录
    path('task', TaskView.as_view(), name='tasks'),
    path('tasks', TasksView.as_view(), name='tasks'),
    path('subtask', SubTaskView.as_view(), name='subtask'),
    path('subtasks', SubTasksView.as_view(), name='subtasks'),
    path('execlists', ExecListsView.as_view(), name='execlists'),
    path('execlist', ExecListView.as_view(), name='execlist'),
    path('execlistlog', ExecListLogView.as_view(), name='execlistlog'),
    path('execlistlogs', ExecListLogsView.as_view(), name='execlistlogs'),
    path('authkey', AuthKEYView.as_view(), name='authkey'),
    path('authkeys', AuthKEYsView.as_view(), name='authkeys'),
    path('project', ProjectView.as_view(), name='project'),
    path('projects', ProjectsView.as_view(), name='projects'),
    path('templatekubernete', TemplateKubernetesView.as_view(), name='templatekubernete'),
    path('templatekubernetes', TemplateKubernetessView.as_view(), name='templatekubernetes'),
    path('templatedb', TemplateDBView.as_view(), name='templatedb'),
    path('templatedbs', TemplateDBsView.as_view(), name='templatedbs'),
    path('tencentservice', TemplateTencentServiceView.as_view(), name='tencentservice'),
    path('tencentservices', TemplateTencentServicesView.as_view(), name='Tencentservices'),
    path('templatenacos', TemplateNacosView.as_view(), name='tencentservice'),
    path('templatenacoses', TemplateNacosesView.as_view(), name='Tencentservices')
]
