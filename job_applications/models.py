from django.db import models

# Create your models here.
class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('AP', 'Applied'),
        ('IN', 'Interview'),
        ('OF', 'Offered'),
        ('RE', 'Rejected'),
    ]

    company = models.CharField(max_length=100)
    date = models.DateField()
    status = models.CharField(max_length=2, choices=STATUS_CHOICES)