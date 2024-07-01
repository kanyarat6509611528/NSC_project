from django.urls import include, path
from app_users import views

urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("register", view=views.register, name="register"),
    path("profile", view=views.profile, name="profile"),
]