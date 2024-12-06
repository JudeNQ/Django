from django.urls import path
from . import views

app_name = "events"
urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create, name="create"),
    path("getall/", views.getall, name="getall"),
    path("getusers/", views.getusers, name="getusers"),
    path("saveEvent/", views.saveevent, name="saveevent")
]