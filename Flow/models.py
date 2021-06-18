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

