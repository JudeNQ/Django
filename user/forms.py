#forms.py is a file that will handle user input (like schedules and user information). 
'''
from django import forms
from .models import Schedule, Event, User

class ScheduleCompareForm(forms.Form):
    # Assuming the schedules have a title and time as fields
    title = forms.CharField(max_length=255, required=True)
    start_time = forms.DateTimeField(required=True)
    end_time = forms.DateTimeField(required=True)

    # Add other fields from the Schedule model that are necessary for comparison

class EventCompareForm(forms.Form):
    # Assuming events have a name, date, and description
    name = forms.CharField(max_length=255, required=True)
    date = forms.DateTimeField(required=True)

class UserCompareForm(forms.Form):
    # Using user model that has a username and email fields
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
'''