FROM python:3.6-alpine
WORKDIR KubernetesManagerWeb
RUN pip install pipenv -i https://pypi.douban.com/simple
RUN pip install djangorestframework -i https://pypi.douban.com/simple
RUN sed -i 's/127.0.0.1/mysql_host/g' KubernetesManagerWeb/settings.py
