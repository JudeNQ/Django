from django.db.models import F, Q
inport re
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from django.conf import settings
from .models import User, Schedule, Event
from .forms import UserCompareForm, ScheduleCompareForm, EventCompareForm


import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login

from rest_framework import generics
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt

#Connect to the server
# Create a new client and connect to the server
uri = "mongodb+srv://cvmccoy123:testtest@cluster0.1tvfg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))

dbname = client['testData']
collection_name = dbname['users']

def index(request):
    return HttpResponse("Hello, world. You're at the user index.")

@csrf_exempt
def create(request):
    if(request.method == 'POST'):
        data = json.loads(request.body) #Parse JSON data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        message = ""
        
        emailPattern = r'^(\w)+@my.unt.edu$'
        
        #Check if the email matches the pattern
        if(re.match(emailPattern, email)):
            print("Valid email")
        else:
            message = "Invalid Email. Make sure you're using a @my.unt.edu email address"
            print("Invalid email")
        
        query = {"email": email}
        item_count = collection_name.count_documents(query)
        
        if(item_count != 0):
            message = "This email is already in use"
        
        # Hash the password using Django's built-in method
        hashed_password = make_password(password)

        # Check if the user already exists (optional but recommended)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already taken'}, status=400)
        
        # Create a new user instance
        user = User(username=username, email=email, password=hashed_password)
        user.save()  # Save the user to the database

        # Omit the raw password in the response for security reasons
        updated_data = {
            'username': username,
            'email': email,
            #'password': password  #Encrypted password (or no password)
            # Do not return or print the raw password for security reasons
        }
        
        return JsonResponse({
            'message': 'User created successfully!',
            'username': username,
            'email': email
        })
        
        #If the message is not the empty string, we know we've had an error
        if(message != ""):
            return JsonResponse(updated_data)
        
        #Attempt to insert the user data into the mongo_db database
        try:
            result = collection_name.insert_one(updated_data)  # Insert into MongoDB
            # Convert ObjectId to string
            updated_data['_id'] = str(result.inserted_id)
            return JsonResponse(updated_data)
        except Exception as e:
            print(f"Error inserting data: {e}")
            return JsonResponse({"error": str(e)}, status=500)
    return HttpResponse("Only PUT requests are valid (Pretty Please)")

        #dbname = client['testData']
        #collection_name = dbname["users"]
        
@csrf_exempt
def login(request):
    if(request.method == 'POST'):
        data = json.loads(request.body) #Parse JSON data
        email = data.get('email')
        password = data.get('password')
        
        query = {"email": email,"password": password}
        
        item_count = collection_name.count_documents(query)
        if item_count != 0:
            updated_data = {
                'email': email,
                'password': password,  #Encrypted password (or no password)
                'confirmed': "True"
            }
        else:
            updated_data = {
                'email': email,
                'password': password,  #Encrypted password (or no password)
                'confirmed': "False"
            }
        return JsonResponse(updated_data)
        try:
            
            #result = collection_name.insert_one(updated_data)  # Insert into MongoDB
            # Convert ObjectId to string
            updated_data['_id'] = str(result.inserted_id)
            return JsonResponse(updated_data)
        except Exception as e:
            print(f"Error inserting data: {e}")
            return JsonResponse({"error": str(e)}, status=500)
    return HttpResponse("Only PUT requests are valid (Pretty Please)")
    return JsonResponse({'error': 'Only POST requests are valid'}, status=400)

# Comaprison views
@csrf_exempt
@api_view(['POST'])
def compare_schedule(request):
    form = ScheduleCompareForm(request.data)
    if form.is_valid():
        title = form.cleaned_data['title']
        start_time = form.cleaned_data['start_time']
        end_time = form.cleaned_data['end_time']

        # Compare schedule with the database using Django ORM
        schedule_matches = Schedule.objects.filter(
            Q(title=title) & Q(start_time=start_time) & Q(end_time=end_time)
        )

        if schedule_matches.exists():
            return JsonResponse({
                'matches': list(schedule_matches.values()), 
                'type': 'Schedule'
            })
        else:
            return JsonResponse({'message': 'No matching schedule found'}, status=404)
    
    return JsonResponse({'error': 'Invalid data'}, status=400)

@csrf_exempt
@api_view(['POST'])
def compare_event(request):
    form = EventCompareForm(request.data)
    if form.is_valid():
        name = form.cleaned_data['name']
        date = form.cleaned_data['date']

        # Compare event with the database
        event_matches = Event.objects.filter(
            Q(name=name) & Q(date=date)
        )

        if event_matches.exists():
            return JsonResponse({
                'matches': list(event_matches.values()), 
                'type': 'Event'
            })
        else:
            return JsonResponse({'message': 'No matching event found'}, status=404)
    
    return JsonResponse({'error': 'Invalid data'}, status=400)

@csrf_exempt
@api_view(['POST'])
def compare_user(request):
    form = UserCompareForm(request.data)
    if form.is_valid():
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']

        # Compare user with the database
        user_matches = User.objects.filter(
            Q(username=username) & Q(email=email)
        )

        if user_matches.exists():
            return JsonResponse({
                'matches': list(user_matches.values()), 
                'type': 'User'
            })
        else:
            return JsonResponse({'message': 'No matching user found'}, status=404)
    
    return JsonResponse({'error': 'Invalid data'}, status=400)