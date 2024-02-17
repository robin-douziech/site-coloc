from django.urls import path
from . import views

app_name = "user"
urlpatterns = [
    path('login', views.login_view, name="login"),
    path('logout', views.logout_view, name="logout"),
    path('change-password', views.change_password, name="change-password"),
    path('create-user', views.create_user, name="create-user"),
]