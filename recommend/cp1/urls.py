from django.urls import path

from . import views, testdb

app_name = 'cp1'
urlpatterns = [
    path('', views.index, name='index'),
    path('db', testdb.testdb, name='testdb'),
]