from django.core.management.base import BaseCommand
from Task.models import Tasks, ExecList, SubTask
import time
import datetime
from lib.Log import RecodeLog
from Task.lib.Log import RecordExecLogs
from Task.lib import ClassImport
from Task.lib.settings import AGENTID, CORPID, SECRET, PARTY


class Command(BaseCommand):
    record_log = RecordExecLogs()

    def handle(self, *args, **options):
        while True:
            for data in Tasks.objects.filter(
                    status__in=['approveing', 'not_start_approve', 'ok_approved']
            ):
                if not self.checkTaskStatus(task=data):
                    continue
                RecodeLog.info(msg='即将开始任务:{}:{}'.format(data.id, data.name))
                self.record_log.task = data
                if not self.runTask(task=data):
                    data.status = 'fail'
                    data.save()
                    massage = '任务失败,任务ID:{},任务名称:{}'.format(data.id, data.name)
                    RecodeLog.error(msg=massage)
                else:
                    data.status = 'success'
                    data.save()
                    massage = '任务完成,任务ID:{},任务名称:{}'.format(data.id, data.name)
                    RecodeLog.info(msg=massage)
                self.alert(message=massage)

    def checkTaskStatus(self, task):
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

    def runTask(self, task):
        if not isinstance(task, Tasks):
            raise TypeError('任务类型错误！')
        task.status = 'progressing'
        task.save()
        for sub in task.sub_task.all():
            self.record_log.sub_task = sub
            self.record_log.project = sub.project
            if not self.runSubTask(subtask=sub):
                task.status = 'fail'
                task.finish_time = datetime.datetime.now()
                task.save()
                return False
        task.status = 'success'
        task.finish_time = datetime.datetime.now()
        task.save()
        return True

    def runSubTask(self, subtask):
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
        for line in subtask.exec_list.all():
            self.record_log.exec_list = line
            if not self.execLine(data=line):
                subtask.status = 'fail'
                subtask.finish_time = datetime.datetime.now()
                subtask.save()
                return False
        subtask.status = 'success'
        subtask.finish_time = datetime.datetime.now()
        subtask.save()
        return True

    def execLine(self, data):
        """
        :param data:
        :return:
        """
        if not isinstance(data, ExecList):
            raise TypeError('任务类型错误！')
        data.status = 'progressing'
        data.save()
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

    def alert(self, message):
        """
        :param message:
        :return:
        """
        import requests
        import json
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={}&corpsecret={}'
        try:
            getr = requests.get(url=url.format(CORPID, SECRET))
            access_token = getr.json().get('access_token')
        except Exception as error:
            RecodeLog.error(msg="获取token失败，{}".format(error))
            return False
        data = {
            "toparty": PARTY,  # 向这些部门发送
            "msgtype": "text",
            "agentid": AGENTID,  # 应用的 id 号
            "text": {
                "content": message
            }
        }
        try:
            r = requests.post(
                url="https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={}".format(access_token),
                data=json.dumps(data)
            )
            if r.json()['errcode'] != 0:
                raise Exception(r.json()['errmsg'])
            RecodeLog.info(msg="发送消息成功:{}".format(r.json()['errmsg']))
            return True
        except Exception as error:
            RecodeLog.info(msg="发送消息失败,{}".format(error))
            return False
