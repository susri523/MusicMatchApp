#forms.py

from django import forms
from django.forms.widgets import DateInput
from .models import UserProfile

class DateInput(forms.DateInput):
    ''' Date picker form input '''
    input_type = 'date'

class Update_UserProfile(forms.ModelForm):

    PRONOUNS = [
        ('HH', 'He/Him/His'),
        ('SS', 'She/Her/Hers'),
        ('TT', 'They/Them/Theirs'),
        ('HT', 'He/They'),
        ('ST', 'She/They'),
        ('AM', 'Please Ask For My Pronouns'),
    ]

    first_name = forms.CharField(max_length=64, label = 'First Name', required=False)
    last_name = forms.CharField(max_length=64, label = 'Last Name', required=False)
    pronouns = forms.ChoiceField(choices= PRONOUNS, label='Pronouns', required=False)
    dob = forms.DateField(widget=DateInput, label='Birthday', required=False)
    
    class Meta:
        """additional data about this form"""
        model = UserProfile #which model to update
        fields = ['first_name', 'last_name', 'pronouns', 'dob'] # which fields to update
