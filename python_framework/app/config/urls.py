from django.contrib import admin
from django.urls import path, re_path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
                  path('', views.ReactView.as_view()),
                  path('admin/', admin.site.urls),
                  path('api/', include('config.api')),

              ] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)
