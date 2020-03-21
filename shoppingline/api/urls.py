from django.contrib import admin
from django.urls import include, path

from shoppingline.api import views

app_name = "api"

urlpatterns = [
    path("auth/login/request/", views.LoginRequestView.as_view()),
    path("auth/login/", views.LoginView.as_view()),
    path("auth/logout/", views.logout),
    path("auth/profile/info/", views.AuthInfoView.as_view()),
    path("auth/profile/update/", views.ProfileUpdateView.as_view()),
    path("webhooks/enqueue-call/", views.enqueue_call),
    path("webhooks/assignment/", views.assignment),
    path("webhooks/events", views.events),
]
