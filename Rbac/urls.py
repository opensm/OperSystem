from django.urls import path
from Rbac.views import AuthView, \
    RoleView, \
    RolesView, \
    PermissionsView, \
    PermissionView, \
    UserView, \
    UsersView, \
    ResetPassWordView

app_name = 'rbac'

urlpatterns = [
    # 用户登录
    path('auth/login', AuthView.as_view(), name='login'),
    # 角色管理
    path('roles', RolesView.as_view(), name='roles'),
    path('role/<int:roleId>', RoleView.as_view(), name='role'),
    # 权限管理
    path('permissions', PermissionsView.as_view(), name='permissions'),
    path('permission/<int:permissionId>', PermissionView.as_view(), name='permission'),
    # 用户管理
    path('users', UsersView.as_view(), name='users'),
    path('user/<int:userId>', UserView.as_view(), name='user'),
    path('resetpass/<int:userId>', ResetPassWordView.as_view(), name='password'),
]
