from __future__ import print_function
import kubernetes.client
from kubernetes.client.rest import ApiException
from Task.models import AuthKEY, TemplateKubernetes, ExecList
from datetime import timedelta, timezone

import time
# from Task.lib.settings import POD_CHECK_KEYS
from Task.lib.Log import RecordExecLogs


class KubernetesClass:
    def __init__(self):
        self.configuration = kubernetes.client.Configuration()
        self.api_apps = None
        self.api_core = None
        self.log = None
        self.limit_time = int(time.time()) - 300

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
            self.log.record(message="认证成功!")
            return True
        except Exception as error:
            self.log.record(message="认证异常！{}".format(error))
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
            self.log.record(message="获取delployment失败:{}!".format(error), status='error')
            return False

    def check_deploy_image(self, deployment, name, exec_list):
        """
        :param deployment:
        :param name:
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
                if containers[i].image != exec_list.params:
                    return False
                else:
                    self.log.record(message="更新镜像与在线镜像一致，跳过更新!".format(containers[i].image))
                    return True
        return False

    def update_deployment(self, namespace, deployment, name, exec_list):
        """
        :param namespace:
        :param deployment:
        :param name:
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
                    self.log.record(message="保存老镜像成功:{}".format(containers[i].image))
                except Exception as error:
                    self.log.record(message="保存老镜像失败:{}".format(error), status='error')
                    return False
                containers[i].image = exec_list.params
                deployment.spec.template.spec.containers = containers
        try:
            self.api_apps.patch_namespaced_deployment(
                namespace=namespace,
                name=name,
                body=deployment
            )
            return True
        except ApiException as e:
            self.log.record(message="更新镜像失败: %s\n" % e, status='error')
            return False

    def check_pods_status(self, namespace, name, label, count=30, replicas=0):
        """
        :param namespace:
        :param name:
        :param label:
        :param count:
        :param replicas
        :return:
        """
        result = True
        self.log.record(message="还剩：{}次尝试次数!".format(count))
        after = self.get_deployment_pods(
            namespace=namespace,
            name=name,
            label=label,
            limit_time=self.limit_time
        )
        self.log.record("获取POD个数:{}".format(after))
        count = count - 1
        if len(after) < replicas and count > 0:
            self.log.record(message="启动pod数不够，现：{}".format(after))
            time.sleep(10)
            return self.check_pods_status(
                namespace=namespace,
                name=name,
                label=label,
                count=count,
                replicas=replicas
            )
        elif len(after) < replicas and count == 0:
            self.log.record(message="检测超时:{}".format(name), status='error')
            return False
        else:
            for x in after:
                status = self.api_core.read_namespaced_pod_status(namespace=namespace, name=x)
                for a in status.status.container_statuses:
                    if not a.ready:
                        result = False
                if not result and count > 0:
                    self.log.record(message="启动pod:{},状态不正确，等待10s，即将下次检测!".format(x))
                    time.sleep(10)
                    return self.check_pods_status(
                        namespace=namespace,
                        name=name,
                        label=label,
                        count=count,
                        replicas=replicas
                    )
                elif not result and count == 0:
                    self.log.record(message="启动pod状态不正确，检测超时，任务失败!", status='error')
                    return False
                else:
                    return True

    def get_deployment_pods(self, namespace, name, label, limit_time=None):
        """
        :param namespace:
        :param name:
        :param label:
        :param limit_time:
        :return:
        """
        data = self.api_core.list_namespaced_pod(
            namespace=namespace,
            label_selector=label.format(name)
        )
        if not limit_time:
            return [x.metadata.name for x in data.items]
        else:
            return [
                x.metadata.name for x in data.items
                if int(time.mktime(
                    x.metadata.creation_timestamp.astimezone(timezone(timedelta(hours=8))).timetuple()
                )) >= limit_time
            ]

    # def check_pod_logs(self, pod, namespace):
    #     """
    #     :param pod:
    #     :param namespace:
    #     :return:
    #     """
    #     data = self.api_core.read_namespaced_pod_log(name=pod, namespace=namespace)
    #     for key in POD_CHECK_KEYS:
    #         if key in data:
    #             # RecodeLog.error(msg="关键字:{},存在日志:{}".format(key, data))
    #             self.log.record(message="关键字:{},存在日志:{}".format(key, data), status='error')
    #             return False
    #         else:
    #             continue
    #     return True

    def run(self, exec_list, logs):
        if not isinstance(exec_list, ExecList):
            raise TypeError("输入任务类型错误！")
        if not isinstance(logs, RecordExecLogs):
            raise TypeError("输入任务类型错误！")

        self.log = logs
        template = exec_list.content_object

        if not isinstance(template, TemplateKubernetes):
            self.log.record(message="传入模板类型错误!", status='error')
            return False
        if not self.connect(obj=template.cluster):
            self.log.record(message="链接K8S集群失败!", status='error')
            return False

        deployment = self.get_deployment(
            deployment_name=template.app_name,
            namespace=template.namespace
        )
        if not deployment:
            self.log.record(message="获取deployment失败!", status='error')
            return False

        if self.check_deploy_image(
                deployment=deployment,
                name=template.app_name,
                exec_list=exec_list
        ):
            return True

        if not self.update_deployment(
                deployment=deployment,
                name=template.app_name,
                namespace=template.namespace,
                exec_list=exec_list
        ):
            self.log.record(message="镜像发布失败：{}".format(exec_list.params))
            return False
        else:
            time.sleep(20)
            if not self.check_pods_status(
                    namespace=template.namespace,
                    name=template.app_name,
                    label=template.label,
                    count=20,
                    replicas=deployment.spec.replicas
            ):
                self.log.record(message="镜像发布失败，容器状态不正确：{}！".format(exec_list.params))
                return False

        #     if not pods:
        #         RecodeLog.error(msg="获取到deployment：{},pod为空，请检查！".format(template.app_name))
        #         return False
        #     for x in pods:
        #         if not self.check_pod_logs(pod=x, namespace=template.namespace):
        #             RecodeLog.error(msg="镜像:{}发布完成，但是Pod:{},存在报错！".format(exec_list.params, x))
        #             return False
        #         else:
        #             RecodeLog.info(msg="镜像:{}发布完成，Pod:{},不存在报错！".format(exec_list.params, x))
        #             continue
        # RecodeLog.info(msg="镜像发布成功！")
        self.log.record(message="镜像发布成功：{}！".format(exec_list.params))
        return True

    def restart(self, exec_list, logs):
        if not isinstance(exec_list, ExecList):
            raise TypeError("输入任务类型错误！")
        if not isinstance(logs, RecordExecLogs):
            raise TypeError("输入任务类型错误！")
        self.log = logs
        template = exec_list.content_object
        if not isinstance(template, TemplateKubernetes):
            self.log.record(message="传入模板类型错误!", status='error')
            return False
        if not self.connect(obj=template.cluster):
            self.log.record(message="链接K8S集群失败!", status='error')
            return False
        deployment = self.get_deployment(
            deployment_name=template.app_name,
            namespace=template.namespace
        )
        if not deployment:
            self.log.record(message="获取deployment失败!", status='error')
            return False
        try:
            self.api_apps.patch_namespaced_deployment(
                namespace=template.namespace,
                name=template.app_name,
                body=deployment
            )
            time.sleep(20)
            if not self.check_pods_status(
                    namespace=template.namespace,
                    name=template.app_name,
                    label=template.label,
                    count=20,
                    replicas=deployment.spec.replicas
            ):
                self.log.record(message="镜像发布失败，容器状态不正确：{}！".format(exec_list.params))
                return False
            return True
        except ApiException as e:
            self.log.record(message="重启deployment失败，原因: %s\n" % e, status='error')
            return False
