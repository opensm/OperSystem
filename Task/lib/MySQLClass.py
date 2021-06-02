# -*- coding: utf-8 -*-
import pymysql
import os
import datetime
from lib.Log import RecodeLog
from Task.lib.settings import DB_BACKUP_DIR
import sys
from Task.lib.lftp import FTPBackupForDB
from Task.lib.base import cmd
from Task.models import AuthKEY, TemplateDB, ExecList


class MySQLClass:
    def __init__(self):
        self.host = None
        self.port = None
        self.user = None
        self.password = None
        self.backup_dir = DB_BACKUP_DIR
        self.auth_str = None
        self.cursor = None
        self.auth_dump_str = None
        if not os.path.exists(self.backup_dir):
            raise Exception(
                "{0} 不存在！".format(self.backup_dir)
            )
        if not os.path.exists("/usr/bin/mysql") or not os.path.exists("/usr/bin/mysqldump"):
            raise Exception("mysql或者mysqldump 没找到可执行程序！")

        self.ftp = FTPBackupForDB(db='mysql')
        self.ftp.connect()

    def connect(self, params):
        """
        :param params:
        :return:
        """
        self.password = params[1]

    def check_db(self, db):
        self.cursor.execute("show databases like '{0}';".format(db))
        res = self.cursor.fetchall()
        if len(res):
            return True
        else:
            RecodeLog.error(msg="数据库：{0},不存在！")
            return False

    def backup_all(self):
        cmd_str = "/usr/bin/mysqldump {0} --all-databases|gzip >{1}".format(
            self.auth_str,
            os.path.join(
                self.backup_dir,
                "{0}-{1}-{2}-all-database.gz".format(
                    self.host, self.port, datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                )
            )

        )
        cmd(cmd_str=cmd_str, replace=self.password)

    def backup_one(self, db, achieve):
        if not self.check_db(db=db):
            sys.exit(1)
        cmd_str = "/usr/bin/mysqldump {0} {1}|gzip >{2}".format(
            self.auth_str,
            db,
            os.path.join(
                self.backup_dir,
                "{}.gz".format(achieve)
            )
        )
        if not cmd(cmd_str=cmd_str, replace=self.password):
            return False
        return True

    def exec_sql(self, db, sql):
        """
        :param db:
        :param sql:
        :return:
        """
        if not os.path.exists(
                os.path.join(self.backup_dir, sql)
        ):
            raise Exception("文件不存在：{0}".format(os.path.join(self.backup_dir, sql)))
        filename, filetype = os.path.splitext(sql)
        if filetype == ".sql":
            cmd_str = "/usr/bin/mysql {0} {1} < {2}".format(
                self.auth_str,
                db,
                os.path.join(self.backup_dir, sql)
            )
        else:
            cmd_str = "zcat {2}|/usr/bin/mysql {0} {1}".format(
                self.auth_str,
                db,
                os.path.join(self.backup_dir, sql)
            )

        if not cmd(cmd_str=cmd_str):
            RecodeLog.error(msg="导入数据失败:{}".format(cmd_str).replace(self.password, '********'))
            return False
        else:
            RecodeLog.info(msg="导入数据成功:{}".format(cmd_str).replace(self.password, '********'))
            return True

    def connect_mysql(self, content):
        """
        :param content:
        :return:
        """
        if not isinstance(content, AuthKEY):
            RecodeLog.error(msg="选择模板错误：{}！".format(content))
            return False
        try:
            self.host = content.auth_host
            self.port = content.auth_port
            self.user = content.auth_user
            self.password = content.auth_passwd
            conn = pymysql.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                connect_timeout=10,
                charset='utf8'
            )
            self.cursor = conn.cursor()
        except Exception as error:
            RecodeLog.error(msg="Mongodb登录验证失败,{}".format(error))
            return False
        self.auth_dump_str = "-u{0} -p{1} -h{2} -P{3} --default-character-set=utf8 ".format(
            self.host, self.port, self.user, self.password
        )
        return True

    def run(self, exec_list):
        """
        :param exec_list:
        :return:
        """
        if not isinstance(exec_list, ExecList):
            raise TypeError("输入任务类型错误！")
        sql = exec_list.params
        if not sql.endswith('.js'):
            RecodeLog.error(msg="输入的文件名错误:{}!".format(sql))
        template = exec_list.content_object
        if not isinstance(template, TemplateDB):
            return False
        if not self.connect_mysql(content=template.instance):
            return False
        filename, filetype = os.path.splitext(sql)
        sql_data = filename.split("#")
        if not self.ftp.download(remote_path=sql_data[2], local_path=self.backup_dir, achieve=sql):
            return False
        if sql_data[1] != 'mysql':
            RecodeLog.error(msg="请检查即将导入的文件的相关信息，{}".format(sql))
            return False
        if len(sql_data) != 4:
            RecodeLog.error(msg="文件格式错误，请按照：20210426111742#mongodb#pre#member.sql")
            return False
        if not self.backup_one(
            db=sql_data[3],
            achieve=filename
        ):
            return False
        if not self.exec_sql(sql=sql, db=sql_data[3]):
            return False
        try:
            exec_list.output = "{}.gz".format(filename)
            exec_list.save()
            RecodeLog.info(msg="保存备份数据情况成功:{}!".format("{}.gz".format(filename)))
            return True
        except Exception as error:
            RecodeLog.error(msg="保存备份数据情况失败:{}!".format(error))
            return False


__all__ = [
    'MySQLClass'
]
