from Task.models import ExecListLog
from lib.Log import RecodeLog


class RecordExecLogs:
    def __init__(self):
        self.task = None
        self.sub_task = None
        self.exec_list = None
        self.project = None

    def record(self, message, status='success'):
        if not self.task or not self.sub_task or not self.exec_list or not self.project:
            raise Exception('初始化内容失败！')
        try:
            ExecListLog.objects.create(
                task=self.task,
                sub_task=self.sub_task,
                exec_flow=self.exec_list,
                project=self.project,
                log=message
            )
            if status == 'success':
                RecodeLog.info(msg=message)
            elif status == 'error':
                RecodeLog.error(msg=message)
            elif status == 'warn':
                RecodeLog.warn(msg=message)
        except Exception as error:
            RecodeLog.error(msg="写入日志失败,日志：{},原因：{}".format(message, error))
