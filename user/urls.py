from django.urls import path
from . import views

app_name = "user"
urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create, name="create"),
    path("login/", views.user_login, name="login"), 

    #Path to the comparison views
    path("compare-schedule/", views.compare_schedule, name="compare_schedule"),
    path("compare-event/", views.compare_event, name="compare_event"),
    path("compare-user/", views.compare_user, name="compare_user"),
]