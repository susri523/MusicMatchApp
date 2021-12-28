import requests

from django.shortcuts import render, redirect 

from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView

from django.contrib import messages
from django.contrib.auth.models import User # the Django User model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .models import UserProfile
from .forms import Update_UserProfile
from .helpers.access_tokens import getUser, getAccessToken, getUserToken, refreshAuth




# Create your views here.
class HomeView(TemplateView):
    '''inherit from generic templateview'''
    template_name = 'musicmatch/about.html'

class TestView(TemplateView):
    '''inherit from generic templateview'''
    template_name = 'musicmatch/test.html'

def auth_spotify(request):
    ''' /authspotify uses the getUser which calls getAuth
        together it puts together a url that is used 
        to make the first api call  '''
    data =  getUser()

    # data to pass through to template
    context = {'data': data}
    print('rendering oauth_callback')
    print(data)
    return render(request,'musicmatch/oauth_callback.html', context)

def callback(request, code=''):
    ''' /callback pathway with GET. this is the 
        redirect uri from spotify and the data that comes 
        from auth_spotify getUser() url first api call, the code 
        that is in the arguments is used to getUserToken() and make
        the second api call. Then we can get the token, set up headers
        and make third api call to get top artist info and user 
        info and check to make sure email is not used already and return'''

    # store A_token, r_token, email, display_name  cookie 

    # retreive str argument from code and supply it to getUserToken     
    code = request.GET.get('code')

    # return render (request, 'musicmatch/test.html', {"code": code})
    getUserToken(str(code))

    #retrieve token list from getAccessToken    
    token = getAccessToken()        #token [a_token, auth_head, scope, expires, r_token]

    #set up r_token and rest of fields as token and parse out the auth_header
    refresh_token = token[4]
    token = token[:4]
    auth_header = token[1]['Authorization']

    #set up header with proper settings for api call 
    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': auth_header,
    }

    #retrieve top_artist response and get the json into data 
    response = requests.get('https://api.spotify.com/v1/me/top/artists', headers=headers)
    data = response.json()

    #retrieve user info response and get the json into userinfo
    response_userinfo = requests.get('https://api.spotify.com/v1/me/', headers=headers)
    userinfo = response_userinfo.json()

    # # open connection to database
    # db = get_db()

    # # query to get email where email matches, to see if email is already in use
    # query = f"SELECT email FROM user_profile where email='{userinfo['email']}'"   
    # usedEmail = db.execute(query)

    # #if email already in use, user is found, redirect back to signup page so user can try again
    # for row in usedEmail:       
    #     if row:
    #         messages.add_message(request, messages.WARNING, 'Email address already exists')

    # #close db connection and return json         
    # close_db()

    #return cookie here 

    # create a form and send it back to the client to fill it in
    form = UserCreationForm()

    context = {
         "userinfo": userinfo, 
         "token": token, 
         "refresh_token": refresh_token,
         "form": form
    }

    # return render(request, 'musicmatch/signup.html',context)    
    return render(request, 'registration/register.html', context)


# Create your views here.
class UpdateProfile(LoginRequiredMixin, UpdateView):
    '''inherit from updateview'''
    model = UserProfile
    form_class = Update_UserProfile
    template_name = 'musicmatch/update_profile.html'
    login_url = '/login/'

class ShowProfilePage(LoginRequiredMixin, DetailView):
    model = UserProfile
    context_object_name = "profile"
    template_name = 'musicmatch/profile_page.html'
    login_url = '/login/'

    def get_object(self):
        
        # this will show the logged-in user's page; if no user logged in, it won't work
        profile = UserProfile.objects.get(user=self.request.user)

        # return this context dictionary
        return profile

@login_required
def getUserTopArtist(request):
    ''' for a given user, retrieves their email and makes 
        an api call to get their top artists and renders 
        and html file for that '''

    profile = UserProfile.objects.get(user=request.user)   
    token, refresh_token = profile.get_tokens()
    

    #set up the auth head to pass in to the header for the api call 
    authorization = f'Bearer {token}'      

    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': authorization,
    }

    #make the api call for top artists and return response to json 
    response = requests.get('https://api.spotify.com/v1/me/top/artists', headers=headers)
    data = response.json()

    #if there is an error then refresh the a_token
    if 'error' in data.keys():

        #call RefreshAuth and get the new_token_info and pick out a_token 
        new_token_info = refreshAuth(refresh_token)
        new_access_token = new_token_info['access_token']

        #update the db with the new a_token for this email pk and commit 
        profile.access_token = new_access_token 
        profile.save()

        # set up auth_head with new token and proper headers
        authorization = f'Bearer {new_access_token}'      

        headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': authorization,
        }

        #make api call to for top artists and store json response in data 
        response = requests.get('https://api.spotify.com/v1/me/top/artists', headers=headers)
        data = response.json()

    #data comes back with items key in dict
    data = data['items']

    #iterate through data.items to retrieve just the name and image url of the artist
    artists = []

    for artist in data:
        name = artist['name']
        url = artist['images'][0]['url']
        artists.append([name, url])
    
    context = {
        "artists": artists,
    }

    return render(request, 'musicmatch/top_artists.html', context)
