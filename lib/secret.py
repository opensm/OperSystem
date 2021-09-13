# coding:utf-8
import base64
from Crypto.Cipher import \
    AES  # 注：python3 安装 Crypto 是 pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pycryptodome<br><br>
from KubernetesManagerWeb.settings import SECRET_KEY
from Crypto.Util.Padding import pad


def pkcs7padding(text):
    """
    明文使用PKCS7填充
    最终调用AES加密方法时，传入的是一个byte数组，要求是16的整数倍，因此需要对明文进行处理
    :param text: 待加密内容(明文)
    :return:
    """
    bs = AES.block_size  # 16
    length = len(text)
    bytes_length = len(bytes(text, encoding='utf-8'))
    # tips：utf-8编码时，英文占1个byte，而中文占3个byte
    padding_size = length if (bytes_length == length) else bytes_length
    padding = bs - padding_size % bs
    # tips：chr(padding)看与其它语言的约定，有的会使用'\0'
    padding_text = chr(padding) * padding
    return text + padding_text


def pkcs7unpadding(text):
    """
    处理使用PKCS7填充过的数据
    :param text: 解密后的字符串
    :return:
    """
    try:
        length = len(text)
        unpadding = ord(text[length - 1])
        return text[0:length - unpadding]
    except Exception as e:
        print('加密异常：{}'.format(e))
        pass


def aes_encode(secret, content):
    """
    AES加密
    key,iv使用同一个
    模式cbc
    填充pkcs7
    :param secret: 密钥
    :param content: 加密内容
    :return:
    """
    key_bytes = bytes(secret, encoding='utf-8')
    iv = key_bytes
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
    # 处理明文
    content_padding = pkcs7padding(content)
    # 加密
    aes_encode_bytes = cipher.encrypt(bytes(content_padding, encoding='utf-8'))
    # 重新编码
    result = str(base64.b64encode(aes_encode_bytes), encoding='utf-8')
    return result


def aes_decode(secret, content):
    """
    AES解密
     key,iv使用同一个
    模式cbc
    去填充pkcs7
    :param secret:
    :param content:
    :return:
    """
    result = None
    try:
        key_bytes = bytes(secret, encoding='utf-8')
        iv = key_bytes
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        # base64解码
        aes_encode_bytes = base64.b64decode(content)
        # 解密
        aes_decode_bytes = cipher.decrypt(aes_encode_bytes)
        # 重新编码
        result = str(aes_decode_bytes, encoding='utf-8')
        # 去除填充内容
        result = pkcs7unpadding(result)
    except Exception as e:
        print('加密异常：{}'.format(e))
        pass
    if not result:
        return False
    else:
        return result


class AesCrypt:
    def __init__(self, model, iv, encode_, key='abcdefghijklmnop'):
        self.encrypt_text = ''
        self.decrypt_text = ''
        self.encode_ = encode_
        self.model = {'ECB': AES.MODE_ECB, 'CBC': AES.MODE_CBC}[model]
        self.key = self.add_16(key)
        if model == 'ECB':
            self.aes = AES.new(self.key, self.model)  # 创建一个aes对象
        elif model == 'CBC':
            self.aes = AES.new(self.key, self.model, iv)  # 创建一个aes对象

        # 这里的密钥长度必须是16、24或32，目前16位的就够用了

    def add_16(self, par):
        par = par.encode(self.encode_)
        while len(par) % 16 != 0:
            par += b'\x00'
        return par

    # 加密
    def aesencrypt(self, text):
        text = pad(text.encode('utf-8'), AES.block_size, style='pkcs7')
        self.encrypt_text = self.aes.encrypt(text)
        return base64.encodebytes(self.encrypt_text).decode().strip()

    # 解密
    def aesdecrypt(self, text):
        text = base64.decodebytes(text.encode(self.encode_))
        self.decrypt_text = self.aes.decrypt(text)
        return self.decrypt_text.decode(self.encode_).strip('\0').strip("\n")


if __name__ == '__main__':
    pr = AesCrypt('ECB', '', 'utf-8', 'abcdefghijklmnop')
    pr1 = AesCrypt("ECB", "", "utf-8")
    en_text = pr.aesencrypt('123456')
    print('密文:', en_text)
    print('明文:', pr1.aesdecrypt(en_text))
