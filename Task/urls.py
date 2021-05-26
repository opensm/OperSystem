from django.urls import path, re_path
from Task.views import *

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
    path('templatekubernetes', TemplateKubernetesView.as_view(), name='templatekubernetes'),
    path('templatekubernetess', TemplateKubernetessView.as_view(), name='templatekubernetess'),
    path('templatedb', TemplateDBView.as_view(), name='templatedb'),
    path('templatedbs', TemplateDBsView.as_view(), name='templatedbs'),
    path('Tencentservice', TemplateDBView.as_view(), name='Tencentservice'),
    path('Tencentservices', TemplateDBsView.as_view(), name='Tencentservices'),
]