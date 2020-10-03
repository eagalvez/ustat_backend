# from django.conf.urls import url 
# from consultas import views 
from django.urls import path
from . import views

urlpatterns = [ 
    # url(r'^consultas/$', views.consultas_list)
    path('', views.consultas_list, name = 'consultas_list')
]