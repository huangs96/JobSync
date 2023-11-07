from django.shortcuts import render
from django.http import HttpResponse
from .models import JobApplication
from .form import JobForm

# Create your views here.
def say_hello(request):
  return render(request, "home.html", {})

# def job_list(request):
#     jobs = JobApplication.objects.all()
#     return render(request, 'home.html', {'jobs': jobs})

# def add_job(request):
#     if request.method == 'POST':
#         form = JobForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('job_list')
#     else:
#         form = JobForm()
#     return render(request, 'templates/add_job.html', {'form': form})

# def first_page(request):
#   return render(request, "JobSync/firstpage.html", {})
