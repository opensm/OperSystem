import json
# python3.6
from http import HTTPStatus
from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote_plus
from urllib.error import HTTPError
# from Task.lib.settings import NOTICE_SETTINGS
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from lib.Log import logger

try:
    import ssl
except ImportError:
    ssl = None


class Sender:
    _address = None

    @staticmethod
    def request(url, method='GET', headers=None, params=None, data=None, files=False):
        """
        :param url:
        :param method:
        :param headers:
        :param params:
        :param data:
        :param files:
        :return:
        """

        # 发送地址链接拼接
        if url.startswith('/'):
            url = url.lstrip('/')
        full_url = "?".join([url, urlencode(params)]) if params else url
        try:
            if files:
                headers = {}
                headers.update({'Content-Type': 'application/zip'})
                data = data
            else:
                data = bytes(data, 'utf8')
            # 初始化请求参数
            req = Request(
                url=full_url, data=data,
                headers=headers, method=method,
            )
            ctx = ssl.SSLContext()
            return urlopen(req, timeout=10, context=ctx)
        except HTTPError as e:
            if e.code in [HTTPStatus.SERVICE_UNAVAILABLE, HTTPStatus.INTERNAL_SERVER_ERROR]:
                logger.error("服务异常，请检查：{}".format(e.reason))
                return False
            else:
                logger.error("严重异常，请检查：{}".format(e.reason))
                return False


class NoticeSender:
    _sender = None
    _sender_config = None
    _write_path = None
    _req = None

    def _get_sender_config(self):
        """
        :return:
        """
        try:
            NOTICE_SETTINGS
        except NameError:
            raise NameError("需要定义：NOTICE_SETTINGS")

        if isinstance(NOTICE_SETTINGS, dict):
            self._sender_config = [NOTICE_SETTINGS]
        elif isinstance(NOTICE_SETTINGS, list):
            self._sender_config = NOTICE_SETTINGS
        else:
            raise TypeError('告警通知配置文件错误，请检查！')
        self._check_notice_config()
        self._req = Sender()

    def _check_notice_config(self):
        """
        :return:
        """

        for config in self._sender_config:
            for key, value in config.items():
                if key not in ['token', 'secret', 'msg_type']:
                    raise KeyError('Error key in config dict!')
                if not value:
                    raise ValueError('Error value for key:{}!'.format(key))

    def dingtalk_sender(self, title, msg, settings: dict, mentioned=None, is_all=True):
        """
        :param title:
        :param msg:
        :param settings:
        :param mentioned:
        :param is_all:
        :return:
        """
        import time
        import base64
        import hmac
        import hashlib
        headers = {'Content-Type': 'application/json'}
        _url = "https://oapi.dingtalk.com/robot/send"
        params = {'access_token': settings['token']}
        if 'secret' in settings.keys():
            timestamp = int(round(time.time() * 1000))
            secret_enc = settings['secret'].encode('utf-8')
            string_to_sign = '{}\n{}'.format(timestamp, settings['secret'])
            string_to_sign_enc = string_to_sign.encode('utf-8')
            hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
            sign = quote_plus(base64.b64encode(hmac_code))
            params['timestamp'] = timestamp
            params['sign'] = sign
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": """## {}\n\n{}""".format(title, msg)
            }
        }
        if is_all or (not is_all and not mentioned):
            at = {
                "isAtAll": is_all
            }
        else:
            if not isinstance(mentioned, list):
                raise TypeError("消息接收人必须为列表!")
            at = {
                "atMobiles": mentioned,
                "isAtAll": is_all
            }
        data['at'] = at

        res = self._req.request(
            url=_url, params=params, data=json.dumps(data),
            headers=headers, method='POST'
        )
        result = json.loads(res.read().decode("UTF-8"))
        if result['errcode'] != 0:
            logger.error("请求异常：{}".format(result['errmsg']))
            return False
        else:
            logger.info("请求成功：{}".format(result['errmsg']))
            return True

    def wechat_sender(self, title, msg, settings: dict, mentioned, is_all=True):
        """
        :param title:
        :param msg:
        :param settings:
        :param mentioned:
        :param is_all:
        :return:
        """

        _url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send"
        params = {'key': settings['token'], 'debug': 1}
        headers = {'Content-Type': 'application/json'}
        if is_all:
            mentioned = ["@all"]
        elif mentioned and not is_all:
            mentioned = mentioned
        else:
            mentioned = []
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": """## {}\n\n {}""".format(title, msg),
                "mentioned_mobile_list": mentioned
            }
        }
        res = self._req.request(
            url=_url, params=params, data=json.dumps(data, ensure_ascii=False), headers=headers, method='POST'
        )
        result = json.loads(res.read().decode("UTF-8"))
        if result['errcode'] != 0:
            logger.error("请求异常：{}".format(result['errmsg']))
            return False
        else:
            logger.info("请求成功：{}".format(result['errmsg']))
            return True

    def create_temp(self, message: str):
        import time

        if not self._write_path:
            self._write_path = './'
        else:
            if not os.path.exists(self._write_path):
                os.makedirs(self._write_path)
        current_files = os.path.join(self._write_path, "{}.txt".format(time.time()))
        try:
            with open(current_files, 'wb') as fff:
                fff.write(str(message).encode('ascii') + b"\n")
            return current_files
        except Exception as error:
            logger.error("创建文件失败:{},{}".format(current_files, error))
            return False

    @staticmethod
    def get_wechat_media(media_file, settings: dict):
        import requests
        _upload_media_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media'
        if not os.path.exists(media_file):
            raise Exception("文件不存在:{}".format(media_file))
        params = {'key': settings['token'], 'type': 'file', 'debug': 1}
        with open(media_file, 'r') as fff:
            try:
                res = requests.post(
                    url="?".join([_upload_media_url, urlencode(params)]) if params else _upload_media_url,
                    files={'file': fff}
                )
            except Exception as error:
                logger.error("读取临时文件失败:{}".format(error))
            return res.json()

    def wechat_file_sender(self, msg: str, settings: dict, mentioned=None, is_all=False):
        if is_all:
            mentioned = ["@all"]
        elif mentioned and not is_all:
            mentioned = mentioned
        else:
            mentioned = []
        _url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send'
        params = {'key': settings['token'], 'type': 'file'}
        headers = {'Content-Type': 'application/json'}
        media_file = self.create_temp(message=msg)
        if not media_file:
            return False

        res = self.get_wechat_media(media_file=media_file, settings=settings)
        data = {
            "msgtype": "file",
            "file": {
                "media_id": res['media_id'],
                "mentioned_mobile_list": mentioned
            }
        }
        res = self._req.request(
            url=_url, method='POST', headers=headers,
            params=params, data=json.dumps(data)
        )
        os.remove(media_file)
        return res

    def dingtalk_file_sender(self):
        pass

    def sender(self, title, msg, mentioned, is_all=False):
        """
        :param title:
        :param msg:
        :param mentioned:
        :param is_all:
        :return:
        """
        thead_list = list()
        self._get_sender_config()
        for setting in self._sender_config:
            with ThreadPoolExecutor(max_workers=3) as worker:
                args = (title, msg, setting, mentioned, is_all)
                if setting['msg_type'] == 'WECHAT_ROBOT':
                    res = worker.submit(self.wechat_sender, *args)
                elif setting['msg_type'] == 'DINGTALK_ROBOT':
                    res = worker.submit(self.dingtalk_sender, *args)
                else:
                    raise Exception('发送类型错误！')
                thead_list.append(res)

        for competed in as_completed(thead_list, timeout=10):
            logger.warning(competed.result())

    def sender_file(self, title, msg, mentioned, is_all=False):
        """
        :param title:
        :param msg:
        :param mentioned:
        :param is_all:
        :return:
        """
        thead_list = list()
        self._get_sender_config()
        for setting in self._sender_config:
            with ThreadPoolExecutor(max_workers=3) as worker:
                args = (title, msg, setting, mentioned, is_all)
                if setting['msg_type'] == 'WECHAT_ROBOT':
                    res = worker.submit(self.wechat_file_sender, *args[1:])
                elif setting['msg_type'] == 'DINGTALK_ROBOT':
                    res = worker.submit(self.dingtalk_sender, *args)
                else:
                    raise Exception('发送类型错误！')
                thead_list.append(res)

        for competed in as_completed(thead_list, timeout=10):
            logger.warning(competed.result())


__all__ = ['NoticeSender']
