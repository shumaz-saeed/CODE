# app/views.py

from django.shortcuts import render
from django.http import HttpResponse # You'll need this if returning simple text

def home(request):# Or, if you want to render a template (which is more common):
     return render(request, 'home.html') # Assuming 'home.html' is in your app/templates/ directory