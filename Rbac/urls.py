from django.urls import path
from Rbac.views import AuthView, RoleView, RolesView

app_name = 'rbac'

urlpatterns = [
    # 用户登录
    path('auth/login', AuthView.as_view(), name='login'),
    # 查询角色
    path('role/add', RolesView.as_view(), name='role')
]
