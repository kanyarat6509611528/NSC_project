from django.urls import include, path

from django.contrib.auth import views as auth_views

from app_users import views

urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("register", views.register, name="register"),
    path("register/thankyou", views.register_thankyou, name="register_thankyou"),
    path("activate/<str:uidb64>/<str:token>", views.activate, name="activate"),
    path("profile", views.profile, name="profile"),
    path('user_select/', views.user_select, name='user_select'),

    # Password reset paths
    path("password_reset/", auth_views.PasswordResetView.as_view(template_name='templates/registrations/password_reset_form.html', 
                                                                 email_template_name='templates/registrations/password_reset_email.html'), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(template_name='templates/registrations/password_reset_done.html'), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name='templates/registrations/password_reset_confirm.html'), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(template_name='templates/registrations/password_reset_complete.html'), name="password_reset_complete"),
]