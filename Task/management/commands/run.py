from django.core.management.base import BaseCommand
from Task.models import Tasks, ExecList, SubTask
import time
import datetime


# from Task.management.commands import ClassImport


class Command(BaseCommand):
    def handle(self, *args, **options):
        while True:
            for data in Tasks.objects.filter(
                    status__in=['approveing', 'not_start_approve', 'ok_approved']
            ):
                if not self.check_task_status(task=data):
                    continue
                self.run_task(task=data)

    def check_task_status(self, task):
        """
        :param task:
        :return:
        """
        local_time = time.time()
        task_unixtime = datetime.datetime.strptime(
            task.task_time,
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ).timestamp()
        if not isinstance(task, Tasks):
            raise TypeError('任务类型错误！')
        if task_unixtime > local_time:
            return False
        elif (local_time - task_unixtime) > 60 * 20:
            task.status = 'timeout'
            task.save()
        elif task_unixtime < local_time and task.status != 'ok_approved':
            return False
        elif task_unixtime < local_time and task.status == 'ok_approved':
            return True

    def run_task(self, task):
        if not isinstance(task, Tasks):
            raise TypeError('任务类型错误！')
        task.status = 'progressing'
        task.save()
        for sub in task.sub_task.all():
            print(111111111111111111111)
            print(sub)
            self.runSubTask(subtask=sub)

    def runSubTask(self, subtask):
        """
        :param subtask:
        :return:
        """
        if not isinstance(subtask, SubTask):
            raise TypeError('任务类型错误！')
        subtask.status = 'progressing'
        subtask.save()

        for line in subtask.exec_list.all():
            print(22222222222222222222222)
            self.execLines(data=line)

    def execLines(self, data):
        """
        :param data:
        :return:
        """
        if not isinstance(data, ExecList):
            raise TypeError('任务类型错误！')
        print(data)
        print(data.content_object)

        # for template in data.content_object:
        #     print()
        #     print(template)
