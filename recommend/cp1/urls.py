from django.urls import path

from . import views

app_name = 'cp1'
urlpatterns = [
    path('', views.index, name='index'),
]