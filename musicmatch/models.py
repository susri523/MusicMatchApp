from django.db import models
from django.contrib.auth.models import User # the Django User model
from django.urls import reverse


# Create your models here.

class UserProfile(models.Model):

    HeHim = 'HH'
    SheHer = 'SS'
    TheyThem = 'TT'
    HeThey = 'HT'
    SheThey = 'ST'
    Ask = 'AM'

    PRONOUNS = [
        (HeHim, 'He/Him/His'),
        (SheHer, 'She/Her/Hers'),
        (TheyThem, 'They/Them/Theirs'),
        (HeThey, 'He/They'),
        (SheThey, 'She/They'),
        (Ask, 'Please Ask For My Pronouns'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True) # each profile is associated with at most one User

    email = models.CharField(max_length = 120)
    first_name = models.CharField(max_length = 64, blank = True)
    last_name = models.CharField(max_length = 64, blank = True)

    #created a drop down menu for selecting a pronoun
    pronouns = models.CharField(max_length=4, choices=PRONOUNS, default=Ask, blank=True)

    dob = models.DateField(null=True, blank=True)
    access_token = models.CharField(max_length = 300, blank = True)
    refresh_token = models.CharField(max_length = 300, blank = True)

    def __str__ (self):
        return f"{self.first_name} - {self.email}"

    def get_absolute_url(self):
        '''Provide a url to show this object'''
        return reverse('profile_page')

    def get_pronouns(self):
        """ Return preferred Pronouns"""

        if self.pronouns == 'HH':
            return 'He/Him/His'
        elif self.pronouns == 'SS':
            return 'She/Her/Hers'
        elif self.pronouns == 'TT':
            return 'They/Them/Theirs'
        elif self.pronouns == 'HT':
            return 'He/They'
        elif self.pronouns == 'ST':
            return 'She/They'
        elif self.pronouns == 'AM':
            return 'Please Ask For My Pronouns'