from rest_framework.views import APIView
from Rbac.models import *
from django.http import JsonResponse


class AuthView(APIView):
    def post(self, request):
        print(request.data)
        return JsonResponse(request.data)

    def get(self, request):
        print(request.data)
        return JsonResponse(request.data)