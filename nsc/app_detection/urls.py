from django.urls import path
from . import views

urlpatterns = [
    path('', views.d_import, name='d01_import'),
    path('loading1', views.d_loading1, name='d02_loading1'),
    path('result', views.d_result, name='d03_result'),
    path('information', views.d_information, name='d03_information'),
    path('select', views.d_select, name='d04_select'),
    path('loading2', views.d_loading2, name='d05_loading2'),
    path('finish', views.d_finish, name='d06_finish'),
]