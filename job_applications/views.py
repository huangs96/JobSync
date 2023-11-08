from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import JobApplication
from .form import JobForm

# Create your views here.
def say_hello(request):
  form = JobForm()
  return render(request, "home.html", {'form': form})

# def job_list(request):
#     jobs = JobApplication.objects.all()
#     return render(request, 'home.html', {'jobs': jobs})

def add_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            jobApplicationSuccess = form.save()
            return redirect('/')
    else:
        form = JobForm()
    return render(request, 'add_job.html', {'form': form})

# def first_page(request):
#   return render(request, "JobSync/firstpage.html", {})
