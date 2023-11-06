from django.urls import path
from job_applications import views

urlpatterns = [
    path("", views.say_hello, name='home')
]