from django.urls import path
from . import views

app_name = "groups"
urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create, name="create"),
    path("getGroups/", views.getGroups, name="getGroups"),
    path("getschedule/", views.getschedule, name="getschedule"),
    path("join/", views.join, name="join"),
]