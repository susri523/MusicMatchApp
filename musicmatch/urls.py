# musicmatch/urls.py

from django.urls import path , include 
from django.conf.urls.static import static
from django.conf import settings
from .views import *


urlpatterns = [
    path('home', HomeView.as_view(), name='home'),  
    path('authspotify', auth_spotify, name='authspotify'),
    path('test', TestView.as_view(), name='test'),  
    path('callback/', callback, name='callback'), 
    path('callback/<str:code>', callback, name='callback'),
    path('complete_profile/<int:pk>', UpdateProfile.as_view(), name='complete_profile'),
    path('profile_page', ShowProfilePage.as_view(), name='profile_page')

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)