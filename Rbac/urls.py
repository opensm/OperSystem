from django.urls import path
from Rbac.views import AuthView, RoleView, RolesView

app_name = 'rbac'

urlpatterns = [
    # 用户登录
    path('auth/login', AuthView.as_view(), name='login'),
    # 查询角色
    path('roles', RolesView.as_view(), name='roles'),
    path('role/<int:roleId>', RoleView.as_view(), name='role')
]
