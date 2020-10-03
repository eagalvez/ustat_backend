# from django.conf.urls import url, include 
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    # url(r'^', include('consultas.urls')),
    path('consultas/', include('consultas.urls')), 
]
