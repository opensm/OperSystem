from django.urls import path, re_path
from Rbac.views import AuthView, \
    RoleView, \
    MenuView, \
    UserView, \
    UsersView, \
    ResetPassWordView, \
    UserStatusEditView, \
    UserEditRoleView, \
    RolePermissionEditView, \
    CurrentUser, \
    LogoutView, \
    DataPermissionsView, \
    DataPermissionView

app_name = 'rbac'

urlpatterns = [
    # 用户登录
    path('login', AuthView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    # 角色管理
    # re_path('^roles$', RolesView.as_view(), name='roles'),
    # re_path('^role/(?P<roleId>[0-9])$', RoleView.as_view()),
    # re_path('^role/(?P<roleId>[0-9])/permission$', RolePermissionEditView.as_view()),
    re_path('^role$', RoleView.as_view()),
    re_path('^role/permission$', RolePermissionEditView.as_view()),
    # 权限管理
    re_path('^menu$', MenuView.as_view(), name='menu'),
    # path('permission/<int:permissionId>', PermissionView.as_view(), name='each_permission_manage'),
    # 数据权限管理
    re_path('^data_permissions$', DataPermissionsView.as_view(), name='data_permission_list_manage'),
    # 用户管理
    # re_path('^users$', UsersView.as_view(), name='users'),
    re_path('^user$', UserView.as_view(), name='user'),
    re_path('^user/reset_passoword$', ResetPassWordView.as_view(), name='reset_passoword'),
    re_path('^user/state$', UserStatusEditView.as_view(), name="user_status"),
    re_path('^user/roles$', UserEditRoleView.as_view(), name="user_role"),
    # re_path('^user/menus$', UserMenu.as_view(), name="user_menu"),
    re_path('^user$', CurrentUser.as_view(), name='user'),
]
