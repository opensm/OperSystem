from Task.models import ExecListLog
from lib.Log import logger


class RecordExecLogs:
    task = None
    sub_task = None
    exec_list = None
    project = None

    def record(self, message):
        kwargs = {
            "task": self.task,
            "sub_task": self.sub_task,
            "exec_list": self.exec_list,
            "project": self.project
        }
        if None in kwargs.values():
            raise ValueError("请检查输入参数是否完整！")

        try:
            ExecListLog.objects.create(**kwargs)
            logger.log(msg=message)
        except Exception as error:
            logger.error(msg="写入日志失败,日志：{},原因：{}".format(message, error))
