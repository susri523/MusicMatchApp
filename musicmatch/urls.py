# musicmatch/urls.py

from django.urls import path , include 
from django.conf.urls.static import static
from django.conf import settings
from .views import HomeView


urlpatterns = [
    path('home', HomeView.as_view(), name='home'),  

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)