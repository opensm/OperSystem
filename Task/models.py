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
    id = models.AutoField(primary_key=True)
    task_id = models.CharField(verbose_name="任务ID", max_length=50, null=False, blank=False, unique=True)
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
    id = models.AutoField(primary_key=True)
    sub_task_id = models.CharField(verbose_name="子任务ID", max_length=50, null=False, blank=False, unique=True)
    status = models.CharField(
        null=False, blank=False, default='not_start_approve', max_length=20, choices=status_choice
    )
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
    id = models.AutoField(primary_key=True)
    auth_type = models.CharField(verbose_name="操作类型", max_length=100, default='Shell')
    exec_account = models.CharField(verbose_name='执行认证方式', max_length=100, default='', null=True)
    exec = models.TextField(verbose_name="执行命令", max_length=2000)
    status = models.CharField(
        null=False, blank=False, default='not_start_approve', max_length=20, choices=status_choice
    )
    create_user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, default='', null=False, blank=False)
    create_time = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)
    finish_time = models.CharField(verbose_name="完成时间", max_length=20, default='', null=True)


class ExecListLog(models.Model):
    id = models.AutoField(primary_key=True)
    exec_flow = models.ForeignKey(ExecList, on_delete=False, null=False, verbose_name='操作')
    log = models.TextField(verbose_name='日志信息')


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
    create_user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, default='', null=False, blank=False)
    create_time = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)
    project = models.ForeignKey('Project', verbose_name='项目', on_delete=models.CASCADE, null=False)


class Project(models.Model):
    id = models.CharField(verbose_name='项目ID', max_length=200, default='', null=False, primary_key=True)
    name = models.CharField(verbose_name='项目ID', max_length=200, default='', null=False)
