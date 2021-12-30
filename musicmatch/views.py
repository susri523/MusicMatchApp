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
from .helpers.genre import genreListConsolidate, compareGenres


# Create your views here.
class HomeView(TemplateView):
    '''inherit from generic templateview'''
    template_name = 'musicmatch/about.html'

class TestView(TemplateView):
    '''inherit from generic templateview'''
    template_name = 'musicmatch/test.html'

####################################################################################
######                           SPOTIFY RELATED                              ###### 
####################################################################################

def auth_spotify(request):
    ''' uses the getUser which calls getAuth. together it creates
        a url that is used to make the first api call  '''

    data =  getUser()

    # data to pass through to template
    context = {'data': data}
    return render(request,'musicmatch/oauth_callback.html', context)

def callback(request, code=''):
    ''' this is the redirect uri from spotify and the data that comes 
        from auth_spotify getUser() url first api call, the code 
        that is in the arguments is used to getUserToken() and make
        the second api call. Then we can get the token, set up headers
        and make third api call to get top artist info and user 
        info and check to make sure email is not used already and return'''

    # retreive str argument from code and supply it to getUserToken     
    code = request.GET.get('code')
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

    # #retrieve top_artist response and get the json into data 
    # response = requests.get('https://api.spotify.com/v1/me/top/artists', headers=headers)
    # data = response.json()

    #retrieve user info response and get the json into userinfo
    response_userinfo = requests.get('https://api.spotify.com/v1/me/', headers=headers)
    # print(response_userinfo)
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

    # create a form and send it back to the client to fill it in
    form = UserCreationForm()

    # pass data through dictionary to render on register page 
    context = {
         "userinfo": userinfo, 
         "token": token, 
         "refresh_token": refresh_token,
         "form": form
    }

    return render(request, 'registration/register.html', context)

####################################################################################
######                           PROFILE RELATED                              ###### 
####################################################################################

class UpdateProfile(UpdateView):
    ''' inherit from updateview and login required and use form class 
        to update the first name, last name, pronouns, dob '''
    model = UserProfile
    form_class = Update_UserProfile
    template_name = 'musicmatch/update_profile.html'
    # login_url = '/login/'

class ShowProfilePage(LoginRequiredMixin, DetailView):
    ''' inherit from detailview and login required and override get_object 
        to show detail view for the logged in user '''
    model = UserProfile
    context_object_name = "profile"
    template_name = 'musicmatch/profile_page.html'
    login_url = '/login/'

    def get_object(self):
        ''' overriden get_object that selects the UserProfile object for the User
            that is logged in 
        '''
        
        # this will show the logged-in user's page; if no user logged in, it won't work
        profile = UserProfile.objects.get(user=self.request.user)
        return profile

####################################################################################
######                        TOP ARTIST RELATED                              ###### 
####################################################################################

def apiCallTopArtist(profile):
    ''' helper function that makes the call for top artist to the API 
        and if there is an error makes the call to get a new access token
        using refresh token and returns the json data 
    '''
    # get the tokens using accessor method 
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

    return data 

@login_required
def getUserTopArtist(request):
    ''' for a given user, retrieves their email and makes an api call 
        to get their top artists and renders and html file for that '''

    # select the profile that is logged in and make the api call for top artist and get json data 
    profile = UserProfile.objects.get(user=request.user)  

    #data comes back with items key in dict
    data = apiCallTopArtist(profile) 
    data = data['items']

    #iterate through data.items to retrieve just the name and image url of the artist
    artists = []

    for artist in data:

        # append the name and url as a list 
        name = artist['name']
        url = artist['images'][0]['url']
        artists.append([name, url])
    
    # pass list of lists of artist [name, url] for each artist to render in the html 
    context = {
        "artists": artists,
    }

    return render(request, 'musicmatch/top_artists.html', context)

def getTopArtist(pk):
    ''' getTopArtist helper function that takes the pk of the UserProfile 
        to make the api call and return the profile and top artists as name, url for each'''

    # get the UserProfile with the given pk 
    profile = UserProfile.objects.get(pk=pk)

    #data comes back with items key in dict
    data = apiCallTopArtist(profile) 
    data = data['items']

    #iterate through data.items to retrieve just the name and image url of the artist
    artists = []

    for artist in data:
        # append the name and url as a list 
        name = artist['name']
        url = artist['images'][0]['url']
        artists.append([name, url])
    
    # profile is a UserProfile object 
    # artists is a list of lists [name, url] for each artist
    return [profile, artists]

####################################################################################
######                           MATCH RELATED                                ###### 
####################################################################################

def getMatchPercent(self_top, other_pk):
    ''' helper function to get match percentages between two users 
        given the logged in users top artists and the other users pk 
        returns the percentage, the other user's profile, the top 3 artists, 
        and the full top artists list for the other user '''

    #use getTopArtist for the other user 
    user, artists = getTopArtist(other_pk) #returns [users, [name, url]]
    # pull out just the names 
    other_top_artist_name = [name for name ,_ in artists]

    #initialize match_count to 0
    match_count = 0

    #first elemet is names of the artist
    for self_top_artist, _ in self_top: 

         # match count increment if found 
         if self_top_artist in other_top_artist_name:
             match_count += 1

    #spotify gives top 20 artists so div by 20 and mult by 100 for %
    percent =  (match_count / 20) * 100
    return [percent, user, artists[:3], artists]

@login_required
def getMatches(request):
    ''' get matches for the logged in user and render the page with 
        matches sorted by match percent for all other users in database'''

    #retrieve the logged in users info 
    profile = UserProfile.objects.get(user=request.user)  

    # get the top artists listing for the logged in user 
    _, self_top_artists = getTopArtist(profile.pk) #returns [user, artists]

    #call helper function to get all the other users in db
    other_users = profile.get_other_users()

    #iterate through the other users and generate their matches
    all_users_top = []
    for user in other_users:

        # get match_percent between the two users 
        user_top_info = getMatchPercent(self_top_artists, user.pk)

        #only append to the beginning of the list if match > 0
        if user_top_info[0] > 0:
            all_users_top.append(user_top_info)

    #if non empty list then sort by match_percent and descending order
    if all_users_top:
        # print(all_users_top)
        all_users_top.sort(reverse=True, key=lambda x: x[0]) #[ match_percent, users, top3, all_top ]

    # pass the profile, list of all matches, percent and their top artist, and the number of matches 
    # to render in html  
    context = {
        "profile": profile, 
        "all_matches": all_users_top,
        "size": len(all_users_top)
    }

    return render(request, "musicmatch/matches.html", context)

class ShowMatchPage(LoginRequiredMixin, DetailView):
    ''' inherit from detailview and login required and use get_context_data
        to supply information about the logged in user, but display data 
        for the UserProfile using the pk  
        to show detail view for the logged in user '''
    model = UserProfile
    context_object_name = "match"
    template_name = 'musicmatch/match_profile_page.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        ''' update the context information to take the logged in
            UserProfile and match_profile value as true so that the
            same html for profile_page can be used for both '''

        context = super(ShowMatchPage, self).get_context_data(**kwargs)

        # this will show the logged-in user's page; if no user logged in, it won't work
        context['profile'] = UserProfile.objects.get(user=self.request.user)
        return context

####################################################################################
######                       GENRE AND EVENT RELATED                          ###### 
####################################################################################
        
def getTopGenres(pk):
    ''' helper function that takes the pk and makes an api call to get 
        the users top genres and return a consolidated list '''

    # get the UserProfile with the given pk 
    profile = UserProfile.objects.get(pk=pk)

    #data comes back with items key in dict
    data = apiCallTopArtist(profile) 
    data = data['items']

    genres = []

    #iterate through data.items to retrieve just the genre of the artist
    for artist in data:
        genres.append(artist['genres'])
    
    # make a list of the users info and the consolidated genre list
    return [profile, genreListConsolidate(genres)]

@login_required
def getEvents(request, pk):
    ''' take the pk of a user and compares their genres with the logged in user
        take the top genre and make a call to ticketmaster api for that genre
        events in Boston (02215) '''

    #retrieve the UserProfile of logged in user and other
    self = UserProfile.objects.get(user=request.user)
    other = UserProfile.objects.get(pk=pk)

    #get top genres for each user 
    _, self_genre = getTopGenres(self.pk) # [users, genres] where genres is a sorted list
    _, other_genre = getTopGenres(other.pk) # [users, genres]

    #compare genres
    genre = compareGenres(self_genre, other_genre)

    # set up a dictionary with the profile as the logged in user and the match as the other user
    context = {         
        "profile": self,
        "match": other
    }

    # if the genre list has more than one genre 
    if len(genre) >= 0:  

        #retrieve the first genre      
        classificationName = genre[0] 

        #enter the classificationName into the api call and get json response back 
        response = requests.get(f"https://app.ticketmaster.com/discovery/v2/events.json?apikey=PBSmqVGp0ZUUCVC3VKJ3oTH3SWnidD7S&classificationName=music&countryCode=US&postalCode=02215&classificationName={classificationName}")
        json_res = response.json()

        # add that genre to the context dict 
        context['genre'] = genre[0]

        #if the response is empty show no_results page
        if json_res["page"]["totalElements"] == 0:
            context['no_events'] = True
            return render(request, 'musicmatch/match_events.html', context)

        #otherwise grab the info from _embedded.events in the reponse and render it 
        else: 
            # add the events list to dict 
            context['events'] = list(json_res["_embedded"]["events"])
          
            return render(request, "musicmatch/match_events.html", context)
    
    #no common umbrella genres 
    context['no_common'] = True

    return render(request, 'musicmatch/match_events.html')