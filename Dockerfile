FROM django
WORKDIR KubernetesManagerWeb
RUN pip install pipenv -i https://pypi.douban.com/simple
RUN pip install djangorestframework -i https://pypi.douban.com/simple
WORKDIR api/
COPY . .
EXPOSE 8080
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]