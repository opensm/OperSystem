# 数据库备份目录
DB_BACKUP_DIR = '/data/db_backup'
# 消息通知
NOTICE_SETTINGS = [
    # notice for wechat
    {'token': ''},
    # notice for dingtalk
    {'token': '', 'secret': ''}
]
# Kubernetes 日志检查关键字段
POD_CHECK_KEYS = [
    'Error',
    'Exception'
]
# 多线程信号量设置（同时开启多少个线程）
SEMAPHORE_COUNT = 0

__all__ = [
    NOTICE_SETTINGS,
    DB_BACKUP_DIR,
    SEMAPHORE_COUNT
]
