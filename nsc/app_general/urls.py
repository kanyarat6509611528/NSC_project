from django.conf import settings 
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('self_test', views.self_test, name='self_test'),
    path('about', views.about, name='about'),
    path('stat', views.stat, name='stat')
] 