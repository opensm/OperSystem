from django.urls import path
from Rbac.views import AuthView

app_name = 'rbac'

urlpatterns = [
    # 用户登录
    path('login', AuthView.as_view(), name='login'),
]
