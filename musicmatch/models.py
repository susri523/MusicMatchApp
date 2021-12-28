from django.db import models
from django.contrib.auth.models import User # the Django User model
from django.urls import reverse

# Create your models here.

class UserProfile(models.Model):
    ''' schema for UserProfile model '''

    # PRONOUNS (stored value, display label)
    PRONOUNS = [
        ('HH', 'He/Him/His'),
        ('SS', 'She/Her/Hers'),
        ('TT', 'They/Them/Theirs'),
        ('HT', 'He/They'),
        ('ST', 'She/They'),
        ('AM', 'Please Ask For My Pronouns'),
    ]

    # using django user field for login so one to one relationship to bind to profile 
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True) 

    #other personal attributes 
    email = models.EmailField(blank=True)
    first_name = models.CharField(max_length = 64, blank = True)
    last_name = models.CharField(max_length = 64, blank = True)
    pronouns = models.CharField(max_length=4, choices=PRONOUNS, default='AM', blank=True)
    dob = models.DateField(null=True, blank=True)

    # spotify token attributes 
    access_token = models.CharField(max_length = 300, blank = True)
    refresh_token = models.CharField(max_length = 300, blank = True)

    def __str__ (self):
        ''' string representation for UserProfile '''
        return f"{self.first_name} - {self.email}"

    def get_absolute_url(self):
        ''' Provide a url to show this object 
            after create and update class based view '''
        return reverse('profile_page')
    
    def get_tokens(self):
        ''' accessor method for both the access token 
            and refresh token for the user '''
        return self.access_token, self.refresh_token 
    
    def get_other_users(self):
        ''' accessor method for all other users in db 
            except logged in user 
        '''
        return UserProfile.objects.all().exclude(pk=self.pk)