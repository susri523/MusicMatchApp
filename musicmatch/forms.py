#forms.py

from django import forms
from django.forms.widgets import DateInput
from .models import UserProfile

class DateInput(forms.DateInput):
    input_type = 'date'

class Update_UserProfile(forms.ModelForm):

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

    first_name = forms.CharField(max_length=64, label = 'First Name', required=False)
    last_name = forms.CharField(max_length=64, label = 'Last Name')
    dob = forms.DateField(widget=DateInput, label='Birthday')
    pronouns = forms.ChoiceField(choices= PRONOUNS, label='Pronouns')

    class Meta:
        """additional data about this form"""
        model = UserProfile #which model to update
        fields = ['first_name', 'last_name', 'pronouns', 'dob'] # which fields to update
