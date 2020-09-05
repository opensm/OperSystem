from rest_framework.views import APIView
from Rbac.models import *


class AuthView(APIView):
    def post(self, request):
        print(request.data)

    def get(self, request):
        print(request.data)
