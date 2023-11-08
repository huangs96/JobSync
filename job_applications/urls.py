from django.urls import path
from job_applications import views

urlpatterns = [
    path("", views.say_hello, name='homepage'),
    path('add-job-posting/', views.add_job, name='add_job_posting')
]