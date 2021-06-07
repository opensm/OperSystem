from __future__ import print_function
import kubernetes.client
from kubernetes.client.rest import ApiException
from Task.models import AuthKEY, TemplateKubernetes, ExecList
from lib.Log import RecodeLog
import time
from Task.lib.settings import POD_CHECK_KEYS


class KubernetesClass:
    def __init__(self):
        self.configuration = kubernetes.client.Configuration()
        self.api_apps = None
        self.api_core = None

    def connect(self, obj):
        if not isinstance(obj, AuthKEY):
            return False
        try:
            self.configuration.api_key = {"authorization": "Bearer " + obj.auth_passwd}
            self.configuration.host = "https://{}:{}".format(obj.auth_host, obj.auth_port)
            self.configuration.verify_ssl = False
            self.configuration.debug = False
            api_client = kubernetes.client.ApiClient(self.configuration)
            self.api_apps = kubernetes.client.AppsV1Api(api_client)
            self.api_core = kubernetes.client.CoreV1Api(api_client)
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
            api_response = self.api_apps.read_namespaced_deployment(
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

    def update_deployment(self, namespace, deployment, name, image, exec_list):
        """
        :param namespace:
        :param deployment:
        :param name:
        :param image:
        :param exec_list:
        :return:
        """
        if not isinstance(exec_list, ExecList):
            raise TypeError("输入任务类型错误！")
        containers = deployment.spec.template.spec.containers
        for i in range(len(containers)):
            if containers[i].name != name:
                continue
            else:
                try:
                    exec_list.output = containers[i].image
                    exec_list.save()
                    RecodeLog.error(msg="保存老镜像成功:{}".format(containers[i].image))
                except Exception as error:
                    RecodeLog.error(msg="保存老镜像失败:{}".format(error))
                    return False
                containers[i].image = image
                deployment.spec.template.spec.containers = containers
        try:
            self.api_apps.patch_namespaced_deployment(
                namespace=namespace,
                name=name,
                body=deployment
            )
            return True
        except ApiException as e:
            RecodeLog.error(msg="更新镜像失败: %s\n" % e)
            return False

    def check_pods_status(self, namespace, name, label, count=30):
        """
        :param namespace:
        :param name:
        :param label:
        :param count:
        :return:
        """
        while count > 0:
            pods = list()
            data = self.api_core.list_namespaced_pod(
                namespace=namespace,
                label_selector=label.format(name)
            )
            for x in data.items:
                if x.status.phase != 'Running':
                    count -= 1
                    time.sleep(2)
                    continue
                pods.append(x.metadata.name)
            return pods

    def check_pod_logs(self, pod, namespace):
        """
        :param pod:
        :param namespace:
        :return:
        """
        data = self.api_core.read_namespaced_pod_log(name=pod, namespace=namespace)
        for key in POD_CHECK_KEYS:
            if key in data:
                RecodeLog.error(msg="关键字:{},存在日志:{}".format(key, data))
                return False
            else:
                continue
        return True

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
                namespace=template.namespace,
                exec_list=exec_list
        ):
            RecodeLog.error(msg="镜像发布失败")
            return False
        else:
            time.sleep(8)
            pods = self.check_pods_status(
                namespace=template.namespace,
                name=template.app_name,
                label=template.label,
                count=20
            )
            if not pods:
                RecodeLog.error(msg="获取到deployment：{},pod为空，请检查！".format(template.app_name))
                return False
            for x in pods:
                if not self.check_pod_logs(pod=x, namespace=template.namespace):
                    RecodeLog.error(msg="镜像:{}发布完成，但是Pod:{},存在报错！".format(exec_list.params, x))
                    return False
                else:
                    RecodeLog.info(msg="镜像:{}发布完成，Pod:{},不存在报错！".format(exec_list.params, x))
                    continue
            RecodeLog.info(msg="镜像发布成功！")
            return True
