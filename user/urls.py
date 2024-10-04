from django.urls import path
from . import views

app_name = "user"
urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create, name="create"),
    path("login/", views.login, name="login")
]