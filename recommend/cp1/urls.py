from django.urls import path

from . import views, testdb, trytry, t2, train

app_name = 'cp1'
urlpatterns = [
    path('', views.index, name='index'),
    path('db', testdb.testdb, name='testdb'),
    path('t2', t2.tt2 , name='t2'),
    path('train', train.traindb , name='train'),
]