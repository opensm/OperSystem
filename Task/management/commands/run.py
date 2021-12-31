from django.core.management.base import BaseCommand
from Task.models import Tasks, ExecList, SubTask, ExecListLog
import time
import datetime
from lib.Log import RecodeLog
from Task.lib.Log import RecordExecLogs
from Task.lib import ClassImport
from Task.lib.settings import AGENTID, CORPID, SECRET, PARTY
from Task.lib.multi_task import MultiSubTask


class Command(BaseCommand):
    record_log = RecordExecLogs()
    t_subtask = MultiSubTask()

    def handle(self, *args, **options):
        while True:
            for data in Tasks.objects.filter(
                    status__in=['approveing', 'not_start_approve', 'ok_approved']
            ):
                if not self.check_task_status(task=data):
                    continue
                RecodeLog.info(msg='即将开始任务:{}:{}'.format(data.id, data.name))
                self.record_log.task = data
                if not self.run_task(task=data):
                    massage = '任务失败：'.format(ExecListLog.objects.filter(task=data).order_by('-id')[0])
                    RecodeLog.error(msg=massage)
                    self.alert(
                        status='失败',
                        title="{}-{}".format(data.id, data.name),
                        message=massage,
                        task_time=data.task_time,
                        finish_time=data.finish_time
                    )
                else:
                    massage = '任务完成!'.format(data.id, data.name)
                    RecodeLog.info(msg=massage)
                    self.alert(
                        status='成功',
                        title="{}-{}".format(data.id, data.name),
                        message=massage,
                        task_time=data.task_time,
                        finish_time=data.finish_time
                    )

    @staticmethod
    def check_task_status(task):
        """
        :param task:
        :return:
        """
        local_time = time.time()
        task_unixtime = datetime.datetime.strptime(
            task.task_time,
            "%Y-%m-%d %H:%M:%S"
        ).timestamp()
        if not isinstance(task, Tasks):
            raise TypeError('任务类型错误！')
        if task_unixtime > local_time:
            return False
        elif (local_time - task_unixtime) > 60 * 20:
            task.status = 'timeout'
            task.save()
            return False
        elif task_unixtime < local_time and task.status != 'ok_approved':
            return False
        elif task_unixtime < local_time and task.status == 'ok_approved':
            return True

    def run_task(self, task):
        if not isinstance(task, Tasks):
            raise TypeError('任务类型错误！')
        task.status = 'progressing'
        task.save()
        # 启动多线程方式并发执行
        if not self.t_subtask.run_bonded_threads(
                sub_tasks=task.sub_task.all(),
                max_threads=5,
                run_function=self.run_subtask
        ):
            task.status = 'fail'
            task.finish_time = datetime.datetime.now()
            task.save()
            return False
        else:
            task.status = 'success'
            task.finish_time = datetime.datetime.now()
            task.save()
            return True

    def run_subtask(self, subtask):
        """
        :param subtask:
        :return:
        """
        if not isinstance(subtask, SubTask):
            raise TypeError('任务类型错误！')
        if subtask.status == 'success':
            return True
        subtask.status = 'progressing'
        subtask.save()
        for line in subtask.exec_list.all().order_by('id'):
            self.record_log.exec_list = line
            if not self.exec_line(data=line):
                subtask.status = 'fail'
                subtask.finish_time = datetime.datetime.now()
                subtask.save()
                return False
        subtask.status = 'success'
        subtask.finish_time = datetime.datetime.now()
        subtask.save()
        return True

    def exec_line(self, data):
        """
        :param data:
        :return:
        """
        if not isinstance(data, ExecList):
            raise TypeError('任务类型错误！')
        data.status = 'progressing'
        data.save()
        if not data.content_object.exec_class:
            self.record_log.record(message="调用类信息错误！", status='error')
            return False
        if not hasattr(ClassImport, data.content_object.exec_class):
            self.record_log.record(message="未检查到该类:{}".format(data.content_object.exec_class), status='error')
            data.status = 'fail'
            data.save()
            return False
        run_class = getattr(ClassImport, data.content_object.exec_class)
        a = run_class()
        run_function = getattr(a, data.content_object.exec_function)
        if not run_function(exec_list=data, logs=self.record_log):
            data.status = 'fail'
            data.finish_time = datetime.datetime.now()
            data.save()
            return False
        else:
            data.status = 'success'
            data.finish_time = datetime.datetime.now()
            data.save()
            return True
