# -*- coding: utf-8 -*-
"""KubernetesManagerWeb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
# from django.conf.urls import url, include
from django.urls import path, include
from django.contrib import admin
from django.views.generic import TemplateView
from Rbac.views import AuthView

urlpatterns = [
    path('admin/', admin.site.urls),
    # url('api/', include(urls)),  # vue前端获取数据的url
    # url('^$', TemplateView.as_view(template_name="index.html")),
    # 验证登录
    path('api/v1/auth/', include("Rbac.urls")),
    path('api/v1/task/', include("Task.urls")),
    path('api/v1/flow/', include("Flow.urls"))
]
