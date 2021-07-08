from Task.serializers import *
from lib.views_v2 import *
from Rbac.serializers import ContentTypeSerializer


class TasksView(BaseListView):
    serializer_class = TaskSerializers
    model_name = 'Tasks'
    app_label = 'Task'
    page_size_query_param = 'limit'
    sort_query_param = 'sort'


class TaskView(BaseDetailView):
    model_name = 'Tasks'
    app_label = 'Task'
    serializer_class = TaskSerializers
    pk = 'id'


class SubTasksView(BaseListView):
    serializer_class = SubTaskSerializers
    model_name = 'SubTask'
    app_label = 'Task'
    page_size_query_param = 'limit'
    sort_query_param = 'sort'


class SubTaskView(BaseDetailView):
    serializer_class = SubTaskSerializers
    model_name = 'SubTask'
    app_label = 'Task'
    pk = 'id'


class ExecListsView(BaseListView):
    serializer_class = ExecListSerializers
    model_name = 'ExecList'
    app_label = 'Task'
    page_size_query_param = 'limit'
    sort_query_param = 'sort'


class ExecListView(BaseDetailView):
    serializer_class = ExecListSerializers
    model_name = 'ExecList'
    app_label = 'Task'
    pk = 'id'


class ExecListLogsView(BaseListView):
    serializer_class = ExecListLogSerializers
    model_name = 'ExecListLog'
    app_label = 'Task'
    page_size_query_param = 'limit'
    sort_query_param = 'sort'


class ExecListLogView(BaseDetailView):
    serializer_class = ExecListLogSerializers
    model_name = 'ExecListLog'
    app_label = 'Task'
    pk = 'id'


class AuthKEYsView(BaseListView):
    serializer_class = AuthKEYSerializers
    model_name = 'AuthKEY'
    app_label = 'Task'
    page_size_query_param = 'limit'
    sort_query_param = 'sort'


class AuthKEYView(BaseDetailView):
    serializer_class = AuthKEYSerializers
    model_name = 'AuthKEY'
    app_label = 'Task'
    pk = 'id'


class ProjectsView(BaseListView):
    serializer_class = ProjectSerializers
    model_name = 'Project'
    app_label = 'Task'
    page_size_query_param = 'limit'
    sort_query_param = 'sort'


class ProjectView(BaseDetailView):
    serializer_class = ProjectSerializers
    model_name = 'Project'
    app_label = 'Task'
    pk = 'id'


class TemplateKubernetessView(BaseListView):
    serializer_class = TemplateKubernetesSerializers
    model_name = 'TemplateKubernetes'
    app_label = 'Task'
    page_size_query_param = 'limit'
    sort_query_param = 'sort'


class TemplateKubernetesView(BaseDetailView):
    serializer_class = TemplateKubernetesSerializers
    model_name = 'TemplateKubernetes'
    app_label = 'Task'
    pk = 'id'


class TemplateDBsView(BaseListView):
    serializer_class = TemplateDBSerializers
    model_name = 'TemplateDB'
    app_label = 'Task'
    page_size_query_param = 'limit'
    sort_query_param = 'sort'


class TemplateDBView(BaseDetailView):
    serializer_class = TemplateDBSerializers
    model_name = 'TemplateDB'
    app_label = 'Task'
    pk = 'id'


class TemplateTencentServicesView(BaseListView):
    serializer_class = TemplateTencentServiceSerializers
    model_name = 'TemplateTencentService'
    app_label = 'Task'
    page_size_query_param = 'limit'
    sort_query_param = 'sort'


class TemplateTencentServiceView(BaseDetailView):
    serializer_class = TemplateTencentServiceSerializers
    model_name = 'TemplateTencentService'
    app_label = 'Task'
    pk = 'id'


class TemplateNacosesView(BaseListView):
    serializer_class = TemplateNacosSerializers
    model_name = 'TemplateNacos'
    app_label = 'Task'
    page_size_query_param = 'limit'
    sort_query_param = 'sort'


class TemplateNacosView(BaseDetailView):
    serializer_class = TemplateNacosSerializers
    model_name = 'TemplateNacos'
    app_label = 'Task'
    pk = 'id'


class TemplateListView(ContentTemplateValueGETView):
    serializer_class = ContentTypeSerializer
    model_name = 'ContentType'
    app_label = 'contenttypes'


__all__ = [
    'TaskView',
    'TasksView',
    'SubTaskView',
    'SubTasksView',
    'ExecListView',
    'ExecListsView',
    'ExecListLogView',
    'ExecListLogsView',
    'AuthKEYView',
    'AuthKEYsView',
    'ProjectView',
    'ProjectsView',
    'TemplateKubernetesView',
    'TemplateKubernetessView',
    'TemplateDBView',
    'TemplateDBsView',
    'TemplateTencentServiceView',
    'TemplateTencentServicesView',
    'TemplateNacosView',
    'TemplateNacosesView',
    'TemplateListView'
]
