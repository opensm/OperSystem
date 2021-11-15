import nacos
from Task.lib.Log import RecordExecLogs
from Task.lib.lftp import FTPBackupForDB
from Task.lib.settings import DB_BACKUP_DIR
import os
from Task.lib.base import cmd
import glob
from Task.models import AuthKEY, ExecList, TemplateNacos
import yaml
import shutil
from KubernetesManagerWeb.settings import SALT_KEY
from lib.secret import AesCrypt


class NacosClass:
    def __init__(self):
        self.nacos = None
        self.log = None
        self.ftp = FTPBackupForDB(db='nacos')
        self.ftp.connect()
        self.backup_dir = DB_BACKUP_DIR

    def upload_config(self, yaml_achieve, config_type):
        """
        :param yaml_achieve:
        :param config_type:
        :return:
        """
        if not os.path.exists(yaml_achieve):
            self.log.record(message="文件不存在:{}".format(yaml_achieve), status='error')
            return False
        data = yaml_achieve.split(os.path.sep)
        try:
            with open(yaml_achieve, 'r') as fff:
                load_dict = yaml.load_all(fff, Loader=yaml.Loader)
                self.nacos.publish_config(
                    content=yaml.dump_all(
                        load_dict,
                        allow_unicode=True
                    ),
                    config_type=config_type,
                    timeout=30,
                    data_id=data[-1],
                    group=data[-2]
                )
        except Exception as error:
            self.log.record(message="上传配置失败:{}".format(error), status='error')
            return False

    def connect_nacos(self, content, namespace):
        """
        :param content:
        :param namespace:
        :return:
        """
        if not isinstance(content, AuthKEY):
            # RecodeLog.error(msg="选择模板错误：{}！".format(content))
            self.log.record(message="选择模板错误：{}！".format(content), status='error')
            return False
        crypt = AesCrypt(model='ECB', iv='', encode_='utf-8', key=SALT_KEY)
        password = crypt.aesdecrypt(content.auth_passwd)
        if not password:
            self.log.record(message='解密密码失败，请检查！', status='error')
            return False
        try:
            if content.auth_port == 443:
                address = 'https://{}:{}'.format(content.auth_host, content.auth_port)
            else:
                address = 'http://{}:{}'.format(content.auth_host, content.auth_port)
            self.nacos = nacos.NacosClient(
                address,
                namespace=namespace,
                username=content.auth_user,
                password=password
            )
            return True
        except Exception as error:
            # RecodeLog.error(msg="登录验证失败,{}".format(error))
            self.log.record(message="登录验证失败,{}".format(error), status='error')
            return False

    def run(self, exec_list, logs):
        """
        :param exec_list:
        :param logs
        :return:
        """

        if not isinstance(exec_list, ExecList):
            raise TypeError("输入任务类型错误！")
        if not isinstance(logs, RecordExecLogs):
            raise TypeError("输入任务类型错误！")
        self.log = logs
        achieve = exec_list.params
        template = exec_list.content_object
        if not isinstance(template, TemplateNacos):
            return False
        if not self.connect_nacos(
                content=template.auth_key,
                namespace=template.namespace
        ):
            return False
        name, extension = os.path.splitext(achieve)
        if extension != '.zip':
            self.log.record(message="文件类型错误:{}".format(achieve), status='error')
            return False
        sql_data = name.split("#")
        if sql_data[1] != 'nacos':
            self.log.record(message="传输文件错误:{}".format(achieve), status='error')
            return False
        # if not self.ftp.download(
        #         remote_path=sql_data[2],
        #         local_path=self.backup_dir,
        #         achieve=achieve
        # ):
        #     return False
        if os.path.exists(os.path.join(self.backup_dir, name)):
            shutil.rmtree(path=os.path.join(self.backup_dir, name))
        unzip_shell_string = 'unzip {} -d {} '.format(
            os.path.join(self.backup_dir, achieve),
            os.path.join(self.backup_dir, name)
        )
        if not cmd(cmd_str=unzip_shell_string, logs=self.log):
            self.log.record(message="解压文件失败：{}".format(unzip_shell_string), status='error')
            return False
        yaml_list = glob.glob(os.path.join(self.backup_dir, name, "*", "*.yaml"))
        if not yaml_list:
            self.log.record(message="导入配置文件为空,请检查！", status='warn')
            return True
        for yml in yaml_list:
            if not self.upload_config(yaml_achieve=yml, config_type=template.config_type):
                self.log.record(message="导入相关配置失败:{}".format(yml), status='error')
                return False
        return True
