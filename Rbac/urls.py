from django.urls import path, re_path
from Rbac.views import AuthView, \
    RoleView, \
    RolesView, \
    PermissionsView, \
    PermissionView, \
    UserView, \
    UsersView, \
    ResetPassWordView, \
    UserStatusEditView, \
    UserEditRoleView

app_name = 'rbac'

urlpatterns = [
    # 用户登录
    path('auth/login', AuthView.as_view(), name='login'),
    # 角色管理
    re_path('role$', RolesView.as_view(), name='roles'),
    path('role/<int:roleId>', RoleView.as_view(), name='role'),
    # 权限管理
    re_path('permission$', PermissionsView.as_view(), name='permissions'),
    path('permission/<int:permissionId>', PermissionView.as_view(), name='permission'),
    # 用户管理
    re_path('user$', UsersView.as_view(), name='users'),
    re_path('user/(?P<userId>[0-9])$', UserView.as_view(), name='user'),
    re_path('user/(?P<userId>[0-9])/reset_passoword$', ResetPassWordView.as_view(), name='password'),
    re_path('user/(?P<userId>[0-9])/state$', UserStatusEditView.as_view(), name="user_status"),
    re_path('user/(?P<userId>[0-9])/roles$', UserEditRoleView.as_view(), name="user_role")
]
