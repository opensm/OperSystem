from django.db import models
from Rbac.models import UserInfo


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
    approve_flow = models.CharField(verbose_name="URL", max_length=200, null=False, blank=False, unique=True)
    status = models.CharField(
        null=False, blank=False, default='not_start_approve', max_length=20, choices=status_choice
    )
    create_user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, default='', null=False, blank=False)
    create_time = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)
    finish_time = models.CharField(verbose_name="完成时间", max_length=20, default='', null=True)
    note = models.TextField(verbose_name="说明", max_length=20000)
    project = models.ForeignKey('Project', verbose_name='项目', on_delete=models.CASCADE, null=False)

    class Meta:
        unique_together = (('parent', 'index'),)
        db_table = 'sys_menus'


class SubTask(models.Model):
    status_choice = (
        ('not_start_exec', '任务还未开始'),
        ('progressing', '任务执行中'),
        ('success', '任务执行成功'),
        ('fail', '任务执行失败')
    )
    id = models.CharField(verbose_name="子任务ID", max_length=50, null=False, blank=False, unique=True, primary_key=True)
    status = models.CharField(
        null=False, blank=False, default='not_start_approve', max_length=20, choices=status_choice
    )
    project = models.ForeignKey('Project', verbose_name='项目', on_delete=models.CASCADE, null=False)
    developer = models.ForeignKey(UserInfo, on_delete=models.CASCADE, null=False)
    create_user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, default='', null=False, blank=False)
    create_time = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)
    finish_time = models.CharField(verbose_name="完成时间", max_length=20, default='', null=True)


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
        ('fail', '任务执行失败')
    )
    exec_type_choice = (
        ('recover', '回档'),
        ('update', '更新')
    )
    id = models.CharField(verbose_name="操作ID", max_length=50, null=False, blank=False, unique=True, primary_key=True)
    auth_type = models.CharField(verbose_name="操作类型", max_length=100, default='Shell')
    auth = models.CharField('AuthKEY', max_length=100, default='', null=True)
    exec = models.TextField(verbose_name="执行命令", max_length=2000, null=True, default='')
    status = models.CharField(
        null=False, blank=False, default='not_start_approve', max_length=20, choices=status_choice
    )
    params = models.CharField(verbose_name='相关参数', max_length=200, null=True, default='')
    exec_type = models.CharField(verbose_name="操作类型", max_length=20, default='update')
    exec_id = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name='执行ID', null=True)
    output = models.TextField(verbose_name="执行结果", null=True, max_length=2000)
    project = models.ForeignKey('Project', verbose_name='项目', on_delete=models.CASCADE, null=False)
    create_user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, default='', null=False, blank=False)
    create_time = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)
    finish_time = models.CharField(verbose_name="完成时间", max_length=20, default='', null=True)


class ExecListLog(models.Model):
    id = models.AutoField(primary_key=True)
    exec_flow = models.ForeignKey(ExecList, on_delete=models.CASCADE, null=False)
    log = models.TextField(verbose_name='日志信息')
    project = models.ForeignKey('Project', verbose_name='项目', on_delete=models.CASCADE, null=False)
    create_time = models.DateTimeField(verbose_name='写入日期', auto_now_add=True)


class AuthKEY(models.Model):
    exec_choice = (
        ('MySQL', 'MySQL'),
        ('Mongo', 'Mongo'),
        ('Shell', 'Shell命令'),
        ('Kubernetes', 'Kubernetes操作')
    )
    id = models.AutoField(primary_key=True)
    auth_type = models.CharField(verbose_name="操作类型", max_length=100, default='Shell', choices=exec_choice)
    auth_key = models.CharField(verbose_name="验证密钥串", max_length=200, default='', null=False)
    name = models.CharField(verbose_name="验证名称", max_length=200, default='', null=False)
    project = models.ForeignKey('Project', verbose_name='项目', on_delete=models.CASCADE, null=False)
    create_user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, default='', null=False, blank=False)
    create_time = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)


class Project(models.Model):
    id = models.CharField(verbose_name='项目ID', max_length=200, default='', null=False, primary_key=True)
    name = models.CharField(verbose_name='项目ID', max_length=200, default='', null=False)
    create_time = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)


class TemplateKubernetes(models.Model):
    control_choice = (
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
    )
    id = models.AutoField(primary_key=True)
    cluster = models.ForeignKey(AuthKEY, on_delete=models.CASCADE, verbose_name='关联集群', null=False)
    namespace = models.CharField(verbose_name='命名空间', null=False, default='system', max_length=100)
    app_name = models.CharField(verbose_name="应用名称", max_length=200, default='', null=False)
    control_type = models.CharField(verbose_name='操作方式', choices=control_choice, max_length=50, default='create')
    yaml = models.TextField(verbose_name='yaml模板', max_length=2000, default='')
    project = models.ForeignKey('Project', verbose_name='项目', on_delete=models.CASCADE, null=False)
    create_user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, default='', null=False, blank=False)
    create_time = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)


class TemplateDB(models.Model):
    id = models.AutoField(primary_key=True)
    mysql_instance = models.ForeignKey(AuthKEY, on_delete=models.CASCADE, verbose_name='实例', null=False)
    exec_line = models.TextField(verbose_name='命令行', max_length=2000, default='')
    project = models.ForeignKey('Project', verbose_name='项目', on_delete=models.CASCADE, null=False)
    create_user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, default='', null=False, blank=False)
    create_time = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)


__all__ = [
    'TemplateDB',
    'Tasks',
    'TemplateKubernetes',
    'SubTask',
    'ExecList',
    'ExecListLog',
    'Project',
    'AuthKEY'
]
