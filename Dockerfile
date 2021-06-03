FROM python:3.6.13
WORKDIR KubernetesManagerWeb
RUN pip install -r requirements.txt  -i https://pypi.douban.com/simple
WORKDIR api/
COPY . .
EXPOSE 8080
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]