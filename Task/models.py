from django.db import models
from Rbac.models import UserInfo
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation


class Tasks(models.Model):
    status_choice = (
        ('approveing', '审批中'),
        ('not_start_approve', '还未审批'),
        ('ok_approved', '审批通过'),
        ('fail_approve', '审批不通过'),
        ('not_start_exec', '任务还未开始'),
        ('progressing', '任务执行中'),
        ('success', '任务执行成功'),
        ('fail', '任务执行失败'),
        ('timeout', '任务已超时'),
        ('unsubmit', '未提交')
    )
    id = models.CharField(verbose_name="任务ID", max_length=50, null=False, blank=False, unique=True, primary_key=True)
    name = models.CharField(verbose_name="任务名称", max_length=200, default='', null=False)
    approve_flow = models.CharField(verbose_name="URL", max_length=200, null=False, blank=False, unique=True)
    status = models.CharField(
        null=False, blank=False, default='not_start_approve', max_length=20, choices=status_choice
    )
    create_user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, default='', null=False, blank=False)
    create_time = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)
    task_time = models.CharField(verbose_name="任务时间", max_length=50, default='', null=True)
    finish_time = models.CharField(verbose_name="完成时间", max_length=20, default='', null=True, blank=True)
    note = models.TextField(verbose_name="说明", max_length=20000)
    project = models.ForeignKey('Project', verbose_name='项目', on_delete=models.CASCADE, null=False)
    sub_task = models.ManyToManyField('SubTask', related_name='subtask')

    class Meta:
        db_table = 't_tasks'


class SubTask(models.Model):
    status_choice = (
        ('not_start_exec', '任务还未开始'),
        ('progressing', '任务执行中'),
        ('success', '任务执行成功'),
        ('fail', '任务执行失败'),
        ('unbond', '任务还未绑定'),
        ('bonded', '任务已绑定')
    )
    id = models.CharField(verbose_name="子任务ID", max_length=50, null=False, blank=False, unique=True, primary_key=True)
    status = models.CharField(
        null=False, blank=False, default='not_start_approve', max_length=20, choices=status_choice
    )
    container = models.CharField(null=False, blank=False, default='', max_length=200)
    project = models.ForeignKey('Project', verbose_name='项目', on_delete=models.CASCADE, null=False)
    developer = models.ForeignKey(UserInfo, on_delete=models.CASCADE, null=False, related_name='developer')
    exec_list = models.ManyToManyField('ExecList', related_name='execlist')
    create_user = models.ForeignKey(
        UserInfo, on_delete=models.CASCADE, default='', null=False, related_name='create_user'
    )
    note = models.TextField(verbose_name="说明", max_length=20000)
    create_time = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)
    finish_time = models.CharField(verbose_name="完成时间", max_length=20, default='', null=True, blank=True)

    class Meta:
        db_table = 't_subtasks'


class ExecList(models.Model):
    exec_choice = (
        ('MySQL', 'MySQL'),
        ('Mongo', 'Mongo'),
        ('Shell', 'Shell命令'),
        ('Kubernetes', 'Kubernetes操作')
    )
    status_choice = (
        ('not_start_exec', '任务还未开始'),
        ('progressing', '任务执行中'),
        ('success', '任务执行成功'),
        ('fail', '任务执行失败'),
        ('recover_not_start_exec', '回档还未开始'),
        ('recover_progressing', '回档执行中'),
        ('recover_success', '回档执行成功'),
        ('recover_fail', '回档执行失败'),
    )
    exec_type_choice = (
        ('recover', '回档'),
        ('update', '更新')
    )
    id = models.CharField(verbose_name="操作ID", max_length=50, null=False, blank=False, unique=True, primary_key=True)
    status = models.CharField(
        null=False, blank=False, default='not_start_approve', max_length=30, choices=status_choice
    )
    params = models.CharField(verbose_name='相关参数', max_length=200, null=True, default='')
    exec_type = models.CharField(verbose_name="操作类型", max_length=20, default='update', choices=exec_type_choice)
    exec_id = models.ForeignKey(
        'self', on_delete=models.CASCADE, verbose_name='执行ID', null=True, related_name='parent_task'
    )
    output = models.TextField(verbose_name="执行结果", null=True, max_length=2000)
    project = models.ForeignKey('Project', verbose_name='项目', on_delete=models.CASCADE, null=False)
    content_type = models.ForeignKey(to=ContentType, on_delete=models.CASCADE)  # 指向ContentType这个模型
    object_id = models.PositiveIntegerField()  # object_id为一个整数，存储了实例id
    content_object = GenericForeignKey(
        'content_type',
        'object_id'
    )  # content_object为GenericForeignKey类型，主要作用是根据content_type字段和object_id字段来定位某个模型中具体某个实例
    create_user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, default='', null=False, blank=False)
    create_time = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)
    finish_time = models.CharField(verbose_name="完成时间", max_length=20, default='', null=True)

    class Meta:
        db_table = 't_execlist'


class ExecListLog(models.Model):
    id = models.AutoField(primary_key=True)
    exec_flow = models.ForeignKey(ExecList, on_delete=models.CASCADE, null=False)
    log = models.TextField(verbose_name='日志信息')
    project = models.ForeignKey('Project', verbose_name='项目', on_delete=models.CASCADE, null=False)
    create_time = models.DateTimeField(verbose_name='写入日期', auto_now_add=True)

    class Meta:
        db_table = 't_execlist_log'


class AuthKEY(models.Model):
    exec_choice = (
        ('MySQL', 'MySQL'),
        ('Mongo', 'Mongo'),
        ('Nacos', 'Nacos'),
        ('Kubernetes', 'Kubernetes操作'),
        ('Qcloud', '腾讯云')
    )
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name="验证名称", max_length=200, default='', null=False)
    auth_host = models.CharField(verbose_name="地址", max_length=200, default='127.0.0.1', null=False)
    auth_port = models.IntegerField(verbose_name="端口", default=22, null=True, blank=True)
    auth_user = models.CharField(verbose_name="验证用户", max_length=200, default='', null=True, blank=True)
    auth_passwd = models.CharField(verbose_name="验证密码", max_length=200, default='', null=True, blank=True)
    auth_params = models.CharField(verbose_name="验证参数", max_length=200, default='', null=True, blank=True)
    auth_type = models.CharField(verbose_name="操作类型", max_length=100, default='Shell', choices=exec_choice)
    project = models.ForeignKey('Project', verbose_name='项目', on_delete=models.CASCADE, null=False)
    create_user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, default='', null=False, blank=False)
    create_time = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)

    class Meta:
        db_table = 't_authkey'


class Project(models.Model):
    id = models.CharField(verbose_name='项目ID', max_length=200, default='', null=False, primary_key=True)
    name = models.CharField(verbose_name='项目名称', max_length=200, default='', null=False)
    create_time = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)

    class Meta:
        db_table = 't_project'


class TemplateKubernetes(models.Model):
    control_choice = (
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
    )
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='模板名称', max_length=200, default='', null=False)
    cluster = models.ForeignKey(AuthKEY, on_delete=models.CASCADE, verbose_name='关联集群', null=False)
    namespace = models.CharField(verbose_name='命名空间', null=False, default='system', max_length=100)
    app_name = models.CharField(verbose_name="应用名称", max_length=200, default='', null=False)
    control_type = models.CharField(verbose_name='操作方式', choices=control_choice, max_length=50, default='create')
    yaml = models.TextField(verbose_name='yaml模板', max_length=2000, default='')
    exec_class = models.TextField(verbose_name='调用类', max_length=2000, default='')
    exec_function = models.TextField(verbose_name='调用方法', max_length=2000, default='')
    exec_list = GenericRelation(to='ExecList')
    create_user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, default='', null=False, blank=False)
    create_time = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)

    class Meta:
        db_table = 't_template_kubernetes'


class TemplateDB(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='模板名称', max_length=200, default='', null=False)
    instance = models.ForeignKey(AuthKEY, on_delete=models.CASCADE, verbose_name='实例', null=False)
    exec_class = models.TextField(verbose_name='调用类', max_length=2000, default='')
    exec_function = models.TextField(verbose_name='调用方法', max_length=2000, default='')
    exec_list = GenericRelation(to='ExecList')
    create_user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, default='', null=False, blank=False)
    create_time = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)

    class Meta:
        db_table = 't_template_db'


class TemplateTencentService(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='模板名称', max_length=200, default='', null=False)
    tencent_key = models.ForeignKey(AuthKEY, on_delete=models.CASCADE, verbose_name='验证信息', null=False)
    exec_class = models.TextField(verbose_name='调用类', max_length=2000, default='')
    exec_function = models.TextField(verbose_name='调用方法', max_length=2000, default='')
    project = models.ForeignKey('Project', verbose_name='项目', on_delete=models.CASCADE, null=False)
    exec_list = GenericRelation(to='ExecList')
    create_user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, default='', null=False, blank=False)
    create_time = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)

    class Meta:
        db_table = 't_template_tencent'


class TemplateNacos(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='模板名称', max_length=200, default='', null=False)
    auth_key = models.ForeignKey(AuthKEY, on_delete=models.CASCADE, verbose_name='实例', null=False)
    exec_class = models.TextField(verbose_name='调用类', max_length=2000, default='')
    exec_function = models.TextField(verbose_name='调用方法', max_length=2000, default='')
    exec_list = GenericRelation(to='ExecList')
    create_user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, default='', null=False, blank=False)
    create_time = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)

    class Meta:
        db_table = 't_template_nacos'


__all__ = [
    'TemplateDB',
    'TemplateTencentService',
    'TemplateNacos',
    'Tasks',
    'TemplateKubernetes',
    'SubTask',
    'ExecList',
    'ExecListLog',
    'Project',
    'AuthKEY'
]
