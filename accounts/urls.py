from django.urls import path

from accounts import views


urlpatterns = [
    path("csrf/", views.csrf_token, name="csrf-token"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("me/", views.profile_view, name="profile"),
]

