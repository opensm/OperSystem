from django.urls import path, re_path
from Rbac.views import *

app_name = 'rbac'

urlpatterns = [
    # 用户登录
    path('login', AuthView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    # 角色管理
    path('roles', RolesView.as_view(), name='roles'),
    path('role', RoleView.as_view()),
    path('role/permission', RolePermissionEditView.as_view()),
    # 权限管理
    path('menus', MenusView.as_view(), name='menus'),
    path('menu', MenuView.as_view(), name='menu'),
    # 数据权限管理
    path('data_permissions', DataPermissionsView.as_view(), name='data_permission_list_manage'),
    path('data_permission', DataPermissionView.as_view(), name='data_permission'),
    # 用户管理
    path('user', UserView.as_view(), name='user'),
    path('users', UsersView.as_view(), name='user'),
    path('user/reset_passoword', ResetPassWordView.as_view(), name='reset_passoword'),
    path('user/state', UserStatusEditView.as_view(), name="user_status"),
    path('user/roles', UserEditRoleView.as_view(), name="user_role"),
    path('current_user', CurrentUserView.as_view(), name='user'),
    path('contenttypes', ContentTypeView.as_view(), name='contenttypes'),
]
