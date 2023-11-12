from django.db import models
from django.utils import timezone

# Create your models here.
class JobApplication(models.Model):

    title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    date_added_to_db = models.DateTimeField(default=timezone.now)
    date_posted = models.DateField()
    date_applied = models.DateField()
    job_url = models.CharField(max_length=100)
    job_description = models.CharField(max_length=1000)
    application_status = models.CharField(
        max_length=20,
        choices=[
            ('applied', 'Applied'),
            ('interview', 'Interview Scheduled'),
            ('offer', 'Job Offered'),
            ('rejected', 'Application Rejected')
        ]
    )

    class Meta:
        app_label = 'job_applications'

    def __str__(self):
        return self.title  # Return the job title as a string representation


