from django import forms
from .models import JobApplication

class JobForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['company', 'job_title', 'date_posted', 'date_applied', 'application_status']
        widgets = {
            'date_posted': forms.DateInput(attrs={'type': 'date'}),
            'date_applied': forms.DateInput(attrs={'type': 'date'})
        }