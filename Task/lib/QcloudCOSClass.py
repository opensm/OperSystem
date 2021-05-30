# -*- coding=utf-8
# appid 已在配置中移除,请在参数 Bucket 中带上 appid。Bucket 由 BucketName-APPID 组成
# 1. 设置用户配置, 包括 secretId，secretKey 以及 Region
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import os
from lib.Log import RecodeLog
from KubernetesManagerWeb.settings import LOG_DIR
import hashlib
from tencentcloud.common import credential


def out_md5(src):
    # 简单封装
    m = hashlib.md5()
    m.update(src)
    return m.hexdigest()


class QcloudCOSClass:
    def __init__(self, auth_key):
        self.tag_file = os.path.join(LOG_DIR, 'cos.tag')
        try:
            cnf = CosConfig(**auth_key)
            self.cred = credential.Credential(auth_key['SecretId'], auth_key['SecretKey'])
            self.client = CosS3Client(cnf)
        except Exception as error:
            RecodeLog.error(msg="初始化COS失败，{0}".format(error))
            sys.exit(1)

    def upload(self, achieve, bucket):
        """
        :param achieve:
        :param bucket:
        :return:
        """
        if not os.path.exists(achieve):
            raise Exception("文件不存在:{}".format(achieve))
        try:
            with open(achieve, 'rb') as fp:
                response = self.client.put_object(
                    Bucket=bucket,
                    Body=fp,
                    Key=os.path.join(os.path.basename(achieve)),
                    StorageClass='STANDARD',
                    EnableMD5=False
                )
                RecodeLog.info(msg=response)
                return True
        except Exception as error:
            RecodeLog.error(msg="文件:{0}，上传失败，原因：{1}".format(os.path.basename(achieve), error))
            return False


__all__ = [
    'QcloudCOSClass'
]
