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
    UserEditRoleView, \
    RolePermissionEditView, \
    UserMenu, \
    CurrentUser

app_name = 'rbac'

urlpatterns = [
    # 用户登录
    path('login', AuthView.as_view(), name='login'),
    path('logout', AuthView.as_view(), name='login'),
    # 角色管理
    re_path('^role$', RolesView.as_view(), name='roles'),
    re_path('^role/(?P<roleId>[0-9])$', RoleView.as_view()),
    re_path('^role/(?P<roleId>[0-9])/permission$', RolePermissionEditView.as_view()),
    # 权限管理
    re_path('^permission$', PermissionsView.as_view(), name='permissions'),
    path('permission/<int:permissionId>', PermissionView.as_view(), name='permission'),
    # 用户管理
    re_path('^users$', UsersView.as_view(), name='users'),
    re_path('^user/(?P<userId>[0-9])$', UserView.as_view(), name='user'),
    re_path('^user/(?P<userId>[0-9])/reset_passoword$', ResetPassWordView.as_view(), name='password'),
    re_path('^user/(?P<userId>[0-9])/state$', UserStatusEditView.as_view(), name="user_status"),
    re_path('^user/(?P<userId>[0-9])/roles$', UserEditRoleView.as_view(), name="user_role"),
    re_path('^user/menus$', UserMenu.as_view(), name="user_menu"),
    re_path('^user$', CurrentUser.as_view(), name='user'),
]
