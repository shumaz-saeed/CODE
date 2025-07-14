from django.urls import path

from django.urls import path
from . import views  # if you're using view.py

urlpatterns = [
    path('', views.home, name='home'),
]
