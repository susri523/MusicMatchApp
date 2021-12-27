from django.shortcuts import render
from django.views.generic import TemplateView, ListView, CreateView


# Create your views here.
class HomeView(TemplateView):
    '''inherit from generic templateview'''
    template_name = 'musicmatch/about.html'
