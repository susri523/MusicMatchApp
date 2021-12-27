import requests

from django.shortcuts import render
from django.views.generic import TemplateView, ListView, CreateView
from django.contrib import messages

from .helpers.access_tokens import getUser, getAccessToken, getUserToken


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

    context = {
         "userinfo": userinfo, 
         "token": token, 
         "refresh_token": refresh_token
    }
    return render(request, 'musicmatch/signup.html',context)

