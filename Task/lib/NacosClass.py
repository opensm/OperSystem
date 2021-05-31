import nacos
from lib.Log import RecodeLog
import sys
import os
from Task.lib.base import cmd
import glob


class NacosClass:
    def __init__(self, params):
        if params['port'] == 443:
            address = 'https://{}:{}'.format(params['host'], params['port'])
        else:
            address = 'http://{}:{}'.format(params['host'], params['port'])
        try:
            self.nacos = nacos.NacosClient(
                address,
                namespace=params['namespace'],
                username=params['user'],
                password=params['passwd']
            )
            self.config_type = params['type']
        except Exception as error:
            RecodeLog.error(msg='初始化失败:{}'.format(error))
            sys.exit(1)

    def upload_config(self, yaml_achieve):
        """
        :param yaml_achieve:
        :return:
        """
        if not os.path.exists(yaml_achieve):
            RecodeLog.error(msg="文件不存在:{}".format(yaml_achieve))
            return False
        data = yaml_achieve.split(os.path.sep)
        try:
            with open(yaml_achieve, 'r') as fff:
                self.nacos.publish_config(
                    content=fff.readlines(),
                    config_type='yaml',
                    timeout=30,
                    data_id=data[-1],
                    group=data[-2]
                )
        except Exception as error:
            RecodeLog.error(msg="上传配置失败:{}".format(error))
            return False

    def run(self, achieve):
        """
        :param achieve:
        :return:
        """
        if not os.path.exists(achieve):
            RecodeLog.error(msg="文件不存在:{}".format(achieve))
            return False
        extension = os.path.splitext(achieve)[-1]
        name = os.path.splitext(achieve)[0]
        if extension != '.zip':
            RecodeLog.error(msg="文件类型错误:{}".format(achieve))
            return False
        unzip_shell_string = 'unzip {} -d {} '.format(achieve, name)
        if not cmd(cmd_str=unzip_shell_string):
            RecodeLog.error(msg="解压文件失败：{}".format(unzip_shell_string))
            return False
        for yml in glob.glob("*/*.yaml"):
            if not self.upload_config(yaml_achieve=yml):
                RecodeLog.error(msg="导入相关配置失败")
                return False
        return True
