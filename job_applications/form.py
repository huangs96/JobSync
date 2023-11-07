from django import forms
from job_applications.models import JobApplication

class JobForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['title', 'company', 'location', 'date_posted', 'date_applied', 'job_url', 'job_description', 'application_status']
        widgets = {
            'date_posted': forms.DateInput(attrs={'type': 'date'}),
            'date_applied': forms.DateInput(attrs={'type': 'date'})
        }