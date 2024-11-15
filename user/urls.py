from django.urls import path
from .views import profile
from . import views

app_name = "user"
urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create, name="create"),
    path("login/", views.login, name="login"),
    path("profile/", views.profile, name="users-profile"),
     path("profile/", views.profile_view, name="profile"),

    #Path to the comparison views
    path("compare-schedule/", views.compare_schedule, name="compare_schedule"),
    path("compare-event/", views.compare_event, name="compare_event"),
    path("compare-user/", views.compare_user, name="compare_user"),

    # Password reset API endpoints
    path('password_reset/', views.password_reset_request, name='password_reset_request'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
]