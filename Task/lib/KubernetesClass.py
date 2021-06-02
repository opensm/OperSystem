from __future__ import print_function
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
        try:
            self.configuration.api_key = {"authorization": "Bearer " + obj.auth_passwd}
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

    def get_deployment(self, deployment_name, namespace):
        """
        :param deployment_name:
        :param namespace:
        :return:
        """
        try:
            api_response = self.api_instance.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
                pretty='true',
                exact=True,
                export=True
            )
            return api_response
        except ApiException as error:
            RecodeLog.error(msg="获取delployment失败:{}!".format(error))
            return False

    def update_deployment(self, namespace, deployment, name, image):
        """
        :param namespace:
        :param deployment:
        :param name:
        :param image:
        :return:
        """
        containers = deployment.spec.template.spec.containers
        for i in range(len(containers)):
            if containers[i].name != name:
                continue
            else:
                containers[i].image = image
                deployment.spec.template.spec.containers = containers
        try:
            api_response = self.api_instance.patch_namespaced_deployment(
                namespace=namespace,
                name=name,
                body=deployment
            )
            RecodeLog.info(msg=api_response)
            return True
        except ApiException as e:
            RecodeLog.error(msg="Exception when calling AppsV1Api->create_namespaced_deployment: %s\n" % e)
            return False

    def run(self, exec_list):
        """
        :param exec_list:
        :return:
        """
        if not isinstance(exec_list, ExecList):
            raise TypeError("输入任务类型错误！")
        template = exec_list.content_object
        if not isinstance(template, TemplateKubernetes):
            RecodeLog.error(msg="传入模板类型错误!")
            return False
        if not self.connect(obj=template.cluster):
            RecodeLog.error(msg="链接K8S集群失败!")
            return False
        deployment = self.get_deployment(
            deployment_name=template.app_name,
            namespace=template.namespace
        )
        if not deployment:
            return False
        if not self.update_deployment(
                deployment=deployment,
                name=template.app_name,
                image=exec_list.params,
                namespace=template.namespace
        ):
            RecodeLog.error(msg="镜像发布失败")
            return False
        else:
            RecodeLog.info(msg="镜像发布成功！")
            return True
