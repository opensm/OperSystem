# -*- coding: utf-8 -*-
import pymysql
import os
import datetime
from lib.Log import RecodeLog
from Task.lib.settings import DB_BACKUP_DIR
import sys
from Task.lib.lftp import FTPBackupForDB


class MySQLClass:
    def __init__(self, auth_key):
        self.host = auth_key['host']
        self.port = auth_key['port']
        self.user = auth_key['user']
        self.password = auth_key['password']
        self.backup_dir = DB_BACKUP_DIR
        self.auth_str = "-u{0} -p{1} -h{2} -P{3} --default-character-set=utf8".format(
            self.user, self.password,
            self.host, self.port
        )
        if not os.path.exists(self.backup_dir):
            raise Exception(
                "{0} 不存在！".format(self.backup_dir)
            )
        if not os.path.exists("/usr/bin/mysql") or not os.path.exists("/usr/bin/mysqldump"):
            raise Exception("mysql或者mysqldump 没找到可执行程序！")
        auth_key['charset'] = "utf8"

        try:
            conn = pymysql.connect(**auth_key)
            self.cursor = conn.cursor()
        except Exception as error:
            RecodeLog.error(msg="链接MySQL,host:{},port:{}失败，原因:{}".format(auth_key['host'], auth_key['port'], error))
            sys.exit(1)

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
        self.cmd(cmd_str=cmd_str)

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
        self.cmd(cmd_str=cmd_str)

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

        if not self.cmd(cmd_str=cmd_str):
            RecodeLog.error(msg="导入数据失败:{}".format(cmd_str).replace(self.password, '********'))
            return False
        else:
            RecodeLog.info(msg="导入数据成功:{}".format(cmd_str).replace(self.password, '********'))
            return True

    def run(self, sql):
        """
        :param sql:
        :return:
        """
        f = FTPBackupForDB(db='mysql')
        filename, filetype = os.path.splitext(sql)
        f.connect()
        sql_data = filename.split("#")
        f.download(remote_path=sql_data[2], local_path=self.backup_dir, achieve=sql)
        if sql_data[1] != 'mysql':
            RecodeLog.error(msg="请检查即将导入的文件的相关信息，{}".format(sql))
            return False
        if len(sql_data) != 4:
            RecodeLog.error(msg="文件格式错误，请按照：20210426111742#mongodb#pre#member.sql")
            return False
        self.backup_one(
            db=sql_data[3],
            achieve=filename
        )
        self.exec_sql(sql=sql, db=sql_data[3])
        return True


__all__ = [
    'MySQLClass'
]
