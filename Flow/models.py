from django.db import models
# from Task.models import Tasks
from Rbac.models import Role


class FlowEngine(models.Model):
    """审批流引擎"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, verbose_name="审批流名称")
    desc = models.TextField(max_length=128, verbose_name="备注")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "工作流引擎"
        verbose_name_plural = verbose_name
        db_table = 't_flow_engine'


class FlowNode(models.Model):
    """
    审批流引擎节点
    """
    id = models.AutoField(primary_key=True)
    flow = models.ForeignKey("FlowEngine", on_delete=models.CASCADE, verbose_name='关联审批流引擎')
    approval_role = models.ForeignKey(to=Role, on_delete=models.CASCADE, verbose_name='审批角色')
    level = models.IntegerField(verbose_name="操作优先级", default=0)

    def __str__(self):
        return self.flow

    class Meta:
        verbose_name = "工作流节点"
        verbose_name_plural = verbose_name
        db_table = 't_flow_node'
        unique_together = (('flow', 'approval_role', 'level'),)


class FlowTask(models.Model):
    """
    审批流任务记录
    """
    approval_choice = (
        ('pass', '通过'),
        ('refuse', '拒绝'),
        ('unprocessed', '未处理')
    )
    id = models.AutoField(primary_key=True)
    # task = models.ForeignKey(Tasks, verbose_name="相关任务", default=0, on_delete=models.CASCADE, null=False)
    task = models.IntegerField(verbose_name="相关任务", default=0, null=False)
    approval_role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True)
    flow = models.ForeignKey("FlowEngine", on_delete=models.CASCADE, null=False, blank=False)
    node = models.ForeignKey("FlowNode", on_delete=models.CASCADE, null=True, blank=True)
    level = models.IntegerField(verbose_name="操作优先级", default=0, null=True, blank=True)
    status = models.CharField(verbose_name="审批状态", default='pass', choices=approval_choice, max_length=20)
    create_time = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)
    finish_time = models.CharField(verbose_name="完成时间", max_length=50, default='', null=True, blank=True)

    class Meta:
        verbose_name = "审批流程"
        verbose_name_plural = verbose_name
        db_table = 't_flow_task'
