# 数据库备份目录
DB_BACKUP_DIR = '/data/db_backup'
FTP_CONFIG = {
    "mongo": {
        "host": "10.92.202.133",
        "port": 2121,
        "user": "mongodb",
        "password": "V7N93k2gxBPOHvXA"
    },
    "mysql": {
        "host": "10.92.202.133",
        "port": 2121,
        "user": "mysql",
        "password": "S8jSS14ParKt9MwY"
    }
}
# 企业微信
SECRET = ""
CORPID = ""
AGENTID = ""
PARTY = ""

__all__ = [
    SECRET,
    CORPID,
    AGENTID,
    PARTY,
    FTP_CONFIG,
    DB_BACKUP_DIR
]
