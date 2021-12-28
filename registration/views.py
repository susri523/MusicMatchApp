##  registration/views.py

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm

import sys
sys.path.append('..')

from musicmatch.models import UserProfile
sys.path.append('/./musicmatch')

def register(request):
    '''
    Respond to registration request and create a new user account.
    '''

    # if this is a "POST", we are processing a form submission, and we will create the User account
    if request.method == "POST":


        # re-create the form object from the request.POST data
        form = UserCreationForm(request.POST)
		
        if form.is_valid():
                        
            email = request.POST.get('email')
            name = request.POST.get('username')  

            # retrieve from cookie 
            token = request.POST.get('token')
            refresh_token = request.POST.get('refresh_token')
			
            # store the new user to the database
            user = form.save()

			
			## this is where you can also create your app-specific user/profile/person type object
            profile = UserProfile(user=user)

            profile.email = email 
            profile.first_name = name
            profile.access_token = token
            profile.refresh_token = refresh_token

            profile.save() # save this new object into the database

            login(request, user)


			# send this user to a complete_profile URL, since they need to add/update information to the newly created profile
            return redirect(reverse("complete_profile", kwargs={"pk":profile.pk}))

        else:
            # show us why it is not valid
            print(form.errors)
            context = {'form': form }

    # if this request is a "GET", it is the first step in the registration process. We will provide the form for the client to fill out and submit.			
    else:
 
        # create a form and send it back to the client to fill it in
        form = UserCreationForm()
        context = {'form': form }
		
    return render(request, "registration/register.html", context)