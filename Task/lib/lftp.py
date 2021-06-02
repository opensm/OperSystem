# -*- coding: utf-8 -*-
from Task.lib.settings import DB_BACKUP_DIR
from ftplib import FTP
from lib.Log import RecodeLog
import sys
import os


class FTPBackupForDB:
    def __init__(self, db="mysql"):
        self.host = FTP_CONFIG[db.lower()]['host']
        self.port = FTP_CONFIG[db.lower()]['port']
        self.user = FTP_CONFIG[db.lower()]['user']
        self.passwd = FTP_CONFIG[db.lower()]['password']
        self.ftp = FTP()

    def connect(self):
        try:
            self.ftp.connect(self.host, self.port)
            self.ftp.login(self.user, self.passwd)
        except Exception as error:
            RecodeLog.error(msg="登录FTP失败：{0}".format(error))
            sys.exit(1)

    def ls_dir(self, path):
        """
        :param path:
        :return:
        """
        self.ftp.set_debuglevel(0)
        self.ftp.cwd(dirname=path)
        return self.ftp.nlst()

    def show_list(self, path):
        """
        :param path:
        :return:
        """
        data = list()
        for x in self.ls_dir(path=path):
            if x == '.' or x == '..':
                continue
            data.append(x)
        return data

    def download(self, remote_path, local_path, achieve):
        """
        :param remote_path:
        :param local_path:
        :param achieve:
        :return:
        """
        bufsize = 1024
        local_file = os.path.join(local_path, achieve)
        achieve_list = self.ls_dir(path=remote_path)
        try:
            if not os.path.exists(local_path):
                raise Exception("本地目录不存在")
            if achieve not in achieve_list:
                raise Exception("远端不存在该文件:{0}".format(achieve_list))
            fp = open(local_file, 'wb')
            self.ftp.retrbinary('RETR ' + achieve, fp.write, bufsize)
            self.ftp.set_debuglevel(0)  # 参数为0，关闭调试模式
            fp.close()
            return True
        except Exception as error:
            RecodeLog.error(msg="上传文件失败，{}，原因：{}".format(local_file, error))
            return False

    def run(self, remote, achieve):
        """
        :param remote:
        :param achieve:
        :return:
        """
        self.connect()
        if not self.download(local_path=DB_BACKUP_DIR, remote_path=remote, achieve=achieve):
            sys.exit(1)
        else:
            sys.exit(0)

    def rm_remote(self, remote, achieve):
        """
        :param remote:
        :param achieve:
        :return:
        """
        remote_achieve = os.path.join(remote, achieve)
        try:
            self.ftp.delete(filename=achieve)
            RecodeLog.info(msg="删除远端文件成功，{}!".format(remote_achieve))
            return True
        except Exception as error:
            RecodeLog.error(msg="删除远端文件失败，{}，原因：{}".format(remote_achieve, error))
            return False

    def __del__(self):
        try:
            self.ftp.dir()
            self.ftp.quit()
        except:
            sys.exit(0)


__all__ = [
    'FTPBackupForDB'
]
