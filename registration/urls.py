# file: registration/urls.py
# description: direct URL requests to view functions

from django.urls import path
from .views import register

urlpatterns = [
    path('register', register, name='register'),

]