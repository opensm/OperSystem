# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import JsonResponse


class JsonResponseServerError(JsonResponse):
    status_code = 500
