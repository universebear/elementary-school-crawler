from django.urls import path
from . import views

urlpatterns = [
    path('', views.BoardListView.as_view()),
    path('select/', views.BoardView.as_view()),
    path('files/', views.BoardFiles.as_view())

]
