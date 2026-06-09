from django.urls import path

from . import views


app_name = "accounts"

urlpatterns = [
    path("login/", views.CustomerLoginView.as_view(), name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.CustomerLogoutView.as_view(), name="logout"),
    path("profile/", views.profile, name="profile"),
    path("orders/", views.orders, name="orders"),
]
