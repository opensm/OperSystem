FROM python:3.6-alpine
WORKDIR KubernetesManagerWeb
RUN pip install pipenv -i https://pypi.douban.com/simple
RUN pip install djangorestframework -i https://pypi.douban.com/simple
