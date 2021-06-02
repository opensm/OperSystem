from __future__ import print_function
import time
import kubernetes.client
from kubernetes.client.rest import ApiException
from pprint import pprint
from Task.models import AuthKEY, TemplateKubernetes, ExecList
from lib.Log import RecodeLog
import base64


class KubernetesClass:
    def __init__(self):
        self.configuration = kubernetes.client.Configuration()
        self.api_instance = None

    def connect(self, obj):
        if not isinstance(obj, AuthKEY):
            return False
        try:
            self.configuration.api_key['authorization'] = {"authorization": "Bearer " + obj.auth_passwd}
            self.configuration.host = "https://{}:{}".format(obj.auth_host, obj.auth_port)
            self.configuration.verify_ssl = False
            self.configuration.debug = False
            api_client = kubernetes.client.ApiClient(self.configuration)
            self.api_instance = kubernetes.client.AppsV1Api(api_client)
            RecodeLog.info(msg="认证成功!")
            return True
        except Exception as error:
            RecodeLog.error(msg="认证异常！{}".format(error))
            return False

    def run(self, exec_list):
        """
        :param exec_list:
        :return:
        """
        if not isinstance(exec_list, ExecList):
            raise TypeError("输入任务类型错误！")
        sql = exec_list.params
        template = exec_list.content_object
        if not isinstance(template, TemplateKubernetes):
            RecodeLog.error(msg="传入模板类型错误!")
            return False
        if not self.connect(obj=template.cluster):
            RecodeLog.error(msg="链接K8S集群失败!")
            return False
        try:
            print(template.namespace)
            print(type(template.namespace))
            namespace = base64.b64encode(bytes(template.namespace, 'UTF-8'))
            api_response = self.api_instance.list_namespaced_deployment(
                namespace=bytes(template.namespace, 'UTF-8')
            )
            pprint(api_response)
        except ApiException as e:
            print("Exception when calling AppsV1Api->create_namespaced_deployment: %s\n" % e)
