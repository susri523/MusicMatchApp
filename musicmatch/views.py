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

def getTopArtist(pk):
    ''' getTopArtist helper function that takes the 
        email of the person to make the api call and 
        return their top artists'''

    profile = UserProfile.objects.get(pk=pk)
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
        profile.token = new_access_token
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
    
    return [profile, artists]

def getMatchPercent(self_top, other_pk):
    ''' helper function to get match percentages 
        between two users with emails used as pk 
        to get data '''

    #use getTopArtist on each user 
    user, artists = getTopArtist(other_pk) #returns [users, name, url]
    other_top_artist_name = [name for name ,_ in artists]

    #initialize match_count to 0
    match_count = 0

    #first elemet is names of top artists and self top artist is each top artist of self
    for self_top_artist, _ in self_top: 

         #other[1] is names of top artists, and if match increment 
         if self_top_artist in other_top_artist_name:
             match_count += 1

    #spotify gives top 20 artists so div by 20 and mult by 100 for %
    percent =  (match_count / 20) * 100
    return [percent, user, artists[:3], artists]

@login_required
def getMatches(request):
    ''' /getMatches asks for a users
        email and uses that to get match percent
        of all users in the database and returns the sorted 
        list of users and their match scores'''

    #retrieve the users info 
    profile = UserProfile.objects.get(user=request.user)  

    _, self_top_artists = getTopArtist(profile.pk) #returns [user, artists]

    #call helper function to get all the other users in db
    other_users = profile.get_other_users()

    #iterature through the other users and generate their matches
    all_users_top = []
    for user in other_users:

        # get match_percent between the two users 
        user_top_info = getMatchPercent(self_top_artists, user.pk)

        #only append to the beginning of the list if match > 0
        if user_top_info[0] > 0:

            #append to the main list 
            all_users_top.append(user_top_info)

    #if non empty list then sort by match_percent and descending order
    if all_users_top:
        all_users_top.sort(reverse=True) #[ match_percent, users, name_top_artists, url_top_artist]

    #get the length of the matches so that it can be used to error check and send info for template
    size = len(all_users_top)

    context = {
        "profile": profile, 
        "all_matches": all_users_top,
        "size": len(all_users_top)
    }

    
    return render(request, "musicmatch/matches.html", context)

class ShowMatchPage(LoginRequiredMixin, DetailView):
    model = UserProfile
    context_object_name = "profile"
    template_name = 'musicmatch/profile_page.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        ''' get logged in users info '''

        context = super(ShowMatchPage, self).get_context_data(**kwargs)

        # this will show the logged-in user's page; if no user logged in, it won't work
        context['self'] = UserProfile.objects.get(user=self.request.user)
        context['match_profile'] = True
        return context
        
def getTopGenres(pk):
    ''' helper function that takes the email and 
        makes an api call to get the users top genres 
        and return a consolidated list '''

    profile = UserProfile.objects.get(pk=pk)
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
        profile.token = new_access_token
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
    genres = []

    #iterate through data.items to retrieve just the genre of the artist
    for artist in data:
        genres.append(artist['genres'])
    

    # make a list of the users info and the consolidated genre list
    return [profile, genreListConsolidate(genres)]

@login_required
def getEvents(request, pk):
    ''' /getEvents path takes 
        both the self and other users emails and compares their genres
        using the list of genres, it takes the first item in the list and 
        makes a call to the ticketmaster api to get events for that genre
        in Boston (02215) 
    '''

    #retrieve the emails of self and other
    self = UserProfile.objects.get(user=request.user)
    other = UserProfile.objects.get(pk=pk)

    #get top genres for each user 
    user_top = getTopGenres(self.pk) # [users, genres] where genres is a sorted list
    other_top = getTopGenres(other.pk) # [users, genres]

    #compare genres
    genre = compareGenres(user_top[1], other_top[1])

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

        context['genre'] = genre[0]
        
        #if the response is empty show no_results page
        if json_res["page"]["totalElements"] == 0:
            context['no_events'] = True
            return render(request, 'musicmatch/match_events.html', context)

        #otherwise grab the info from _embedded.events in the reponse and render it 
        else: 
            context['events'] = list(json_res["_embedded"]["events"])
          
            return render(request, "musicmatch/match_events.html", context)
    
    #no common umbrella genres 
    context['no_common'] = True

    return render(request, 'musicmatch/match_events.html')