from django.urls import path
from job_applications import views

urlpatterns = [
    path("", views.job_list, name='jobs'),
    path('add-job-posting/', views.add_job, name='add_job_posting')
]