from django.urls import path, include

urlpatterns = [
    path('board/', include('boards.urls')),

]
