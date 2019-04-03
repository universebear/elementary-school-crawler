from django.views.generic import View
from django.http import HttpResponse
from django.conf import settings
import os


class ReactView(View):
    def get(self, request):
        try:
            with open(os.path.join(str(settings.BASE_DIR), 'frontend', 'build', 'index.html')) as file:
                return HttpResponse(file.read())
        except:
            return HttpResponse('index.html is not found, build your React app', status=501)
