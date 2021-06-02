# KubernetesManagerWeb
Kubernetes管理页面
### 项目初始化 __init__.py
import pymysql
pymysql.version_info = (1, 4, 13, "final", 0)
pymysql.install_as_MySQLdb()
### Kubernetes权限设置
```
apiVersion: v1
kind: ServiceAccount
metadata:
  creationTimestamp: null
  name: jenkins
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  # "namespace" 被忽略，因为 ClusterRoles 不受名字空间限制
  name: system-oper-cr
  namespace: default
rules:
- apiGroups: ["apps"]
  # 在 HTTP 层面，用来访问 Secret 对象的资源的名称为 "secrets"
  resources: ["deployments"]
  verbs: ["get", "watch", "list", "patch"]
apiVersion: rbac.authorization.k8s.io/v1
# 此角色绑定使得用户 "dave" 能够读取 "default" 名字空间中的 Secrets
# 你需要一个名为 "secret-reader" 的 ClusterRole
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: system-oper-rb
  # RoleBinding 的名字空间决定了访问权限的授予范围。
  # 这里仅授权在 "development" 名字空间内的访问权限。
  namespace: default
subjects:
- kind: ServiceAccount
  name: jenkins # 'name' 是不区分大小写的
  namespace: default
- kind: User
  name: jenkins
  namespace: default
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: system-oper-cr
  apiGroup: rbac.authorization.k8s.io
```