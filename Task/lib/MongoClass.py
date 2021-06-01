# -*- coding: utf-8 -*-
import pymongo
import datetime
import os
from Task.lib.settings import DB_BACKUP_DIR
from lib.Log import RecodeLog
import sys
from Task.lib.lftp import FTPBackupForDB
from Task.lib.base import cmd
from Task.models import ExecList


class MongoClass:
    def __init__(self, auth_key):
        self.host = auth_key['host']
        self.port = auth_key['port']
        self.user = auth_key['user']
        self.password = auth_key['password']
        self.auth_dump_str = "--host {} --port {} -u {} -p {}  --authenticationDatabase admin ".format(
            self.host, self.port,
            self.user, self.password
        )
        if not os.path.exists(DB_BACKUP_DIR):
            raise Exception(
                "{0} 不存在！".format(DB_BACKUP_DIR)
            )
        if not os.path.exists("/usr/bin/mongodump") or not os.path.exists("/usr/bin/mongorestore"):
            raise Exception("mongo或者mongodump, mongorestore没找到可执行程序！")

        try:
            self.conn = pymongo.MongoClient(host=self.host, port=self.port, username=self.user, password=self.password)
        except Exception as error:
            RecodeLog.error(msg="链接Mongo,host:{},port:{}失败，原因:{}".format(auth_key['host'], auth_key['port'], error))
            sys.exit(1)

    def check_db(self, db):
        res = self.conn.list_database_names()
        if db in res:
            return True
        else:
            RecodeLog.error(msg="数据库：{0},不存在！".format(db))
            return False

    def backup_all(self):
        cmd_str = "/usr/bin/mongodump {0} --gzip --archive={1}".format(
            self.auth_dump_str,
            os.path.join(
                DB_BACKUP_DIR,
                "mongo-{0}-{1}-{2}-all-database.gz".format(
                    self.host, self.port, datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                )
            )
        )
        cmd(cmd_str=cmd_str, replace=self.password)

    def backup_one(self, db, achieve):
        if not self.check_db(db=db):
            return
        cmd_str = "/usr/bin/mongodump {0}  --gzip --archive={2}".format(
            self.auth_dump_str,
            db,
            os.path.join(
                DB_BACKUP_DIR,
                "{}.gz".format(achieve)
            )
        )
        if not cmd(cmd_str=cmd_str, replace=self.password):
            return False
        else:
            return True

    def exec_sql(self, db, sql):
        """
        :param db:
        :param sql:
        :return:
        """
        if not os.path.exists(
                os.path.join(DB_BACKUP_DIR, sql)
        ):
            raise Exception("文件不存在：{0}".format(os.path.join(DB_BACKUP_DIR, sql)))
        filename, filetype = os.path.splitext(sql)
        if filetype == ".js":
            cmd_str = "/usr/bin/mongo {0} {1}  {2}".format(
                self.auth_dump_str,
                db,
                os.path.join(DB_BACKUP_DIR, sql)
            )
        elif filetype == ".gz":
            cmd_str = "zcat {2}|/usr/bin/mongorestore {0} {1} --archive".format(
                self.auth_dump_str,
                db,
                os.path.join(DB_BACKUP_DIR, sql)
            )
        else:
            RecodeLog.error(msg="不能识别的文件类型:{}".format(sql))
            return False
        if not cmd(cmd_str=cmd_str, replace=self.password):
            RecodeLog.error(msg="导入数据失败:{}".format(cmd_str).replace(self.password, '********'))
            return False
        else:
            RecodeLog.info(msg="导入数据成功:{}".format(cmd_str).replace(self.password, '********'))
            return True

    def run(self, exec_list):
        """
        :param exec_list:
        :return:
        """
        if not isinstance(exec_list, ExecList):
            raise TypeError("输入任务类型错误！")
        sql = ExecList.params
        if not sql.endswith('.js'):
            RecodeLog.error(msg="输入的文件名错误:{}!".format(sql))
        f = FTPBackupForDB(db='mongo')
        filename, filetype = os.path.splitext(sql)
        f.connect()
        sql_data = filename.split("#")
        f.download(remote_path=sql_data[2], local_path=DB_BACKUP_DIR, achieve=sql)
        sql_data = filename.split("#")
        if sql_data[1] != 'mongodb':
            RecodeLog.error(msg="请检查即将导入的文件的相关信息，{}".format(sql))
            return False
        if len(sql_data) != 4:
            RecodeLog.error(msg="文件格式错误，请按照：20210426111742#mongodb#pre#member.js")
            return False
        self.backup_one(
            db=sql_data[3],
            achieve=filename
        )
        self.exec_sql(sql=sql, db=sql_data[3])
        return True


__all__ = [
    'MongoClass'
]
