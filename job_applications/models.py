from django.db import models

# Create your models here.
class JobApplication(models.Model):

    company = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    date_posted = models.DateField()
    date_applied = models.DateField()
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
        return self.job_title  # Return the job title as a string representation


