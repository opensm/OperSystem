from __future__ import print_function
import time
import kubernetes.client
from kubernetes.client.rest import ApiException
from pprint import pprint
from Task.models import AuthKEY, TemplateKubernetes, ExecList
from lib.Log import RecodeLog


class KubernetesClass:
    def __init__(self):
        self.configuration = kubernetes.client.Configuration()
        self.api_instance = None

    def connect(self, obj):
        if not isinstance(obj, AuthKEY):
            return False
        self.configuration.api_key['authorization'] = obj.auth_passwd
        self.configuration.host = "https://{}:{}".format(obj.auth_host, obj.auth_port)
        api_client = kubernetes.client.ApiClient(self.configuration)
        self.api_instance = kubernetes.client.AppsV1Api(api_client)

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
            return False
        if not self.connect(obj=template.cluster):
            return False
        try:
            api_response = self.api_instance.list_namespaced_deployment(
                template.namespace
            )
            pprint(api_response)
        except ApiException as e:
            print("Exception when calling AppsV1Api->create_namespaced_deployment: %s\n" % e)
