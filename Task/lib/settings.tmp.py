# 数据库备份目录
DB_BACKUP_DIR = '/data/db_backup'
FTP_CONFIG = {
    "mongo": {
        "host": "",
        "port": 2121,
        "user": "",
        "password": ""
    },
    "mysql": {
        "host": "",
        "port": 2121,
        "user": "",
        "password": ""
    },
    "nacos": {
        "host": "",
        "port": 2121,
        "user": "",
        "password": ""
    }
}
# 企业微信
SECRET = ""
CORPID = ""
AGENTID = ""
PARTY = ""
# Kubernetes 日志检查关键字段
POD_CHECK_KEYS = [
    'Error',
    'Exception'
]

__all__ = [
    SECRET,
    CORPID,
    AGENTID,
    PARTY,
    FTP_CONFIG,
    DB_BACKUP_DIR
]
