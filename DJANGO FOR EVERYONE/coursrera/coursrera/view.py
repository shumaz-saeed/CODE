from django.shortcuts import render

def home(request):
    return render(request, 'cousrera/template/home.html')
