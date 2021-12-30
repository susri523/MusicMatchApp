# musicmatch/urls.py

from django.urls import path , include 
from django.conf.urls.static import static
from django.conf import settings
from .views import *


urlpatterns = [
    # home page and spotify related 
    path('home', HomeView.as_view(), name='home'),  
    path('authspotify', auth_spotify, name='authspotify'),
    path('callback/', callback, name='callback'), 
    path('callback/<str:code>', callback, name='callback'),

    # base view to check if path is working 
    path('test', TestView.as_view(), name='test'),  

    # update profile and view profile page 
    path('complete_profile/<int:pk>', UpdateProfile.as_view(), name='complete_profile'),
    path('profile_page', ShowProfilePage.as_view(), name='profile_page'),

    # top artists, matches, match profile page, events page 
    path('top_artists', getUserTopArtist,name='top_artists'),
    path('matches', getMatches, name='matches'),
    path('match_user_page/<int:pk>', ShowMatchPage.as_view(), name='match_user_page'),
    path('get_events/<int:pk>', getEvents, name='match_events'),

    # logged in user making friend request
    path('friend_request/<int:pk>', makeFriendRequest, name='friend_request'),
    # logged in user accepts friend request
    path('accept_request/<int:pk>', acceptFriendRequest, name='accept_request'),



]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)