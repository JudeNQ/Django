from django.shortcuts import render
import re
from django.db.models import F
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from django.conf import settings
from datetime import datetime
import json
from django.http import JsonResponse

from rest_framework import generics
from django.views.decorators.csrf import csrf_exempt

#Connect to the server
# Create a new client and connect to the server
uri = "mongodb+srv://cvmccoy123:testtest@cluster0.1tvfg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))

dbname = client['testData']
collection_name = dbname['events']

def index(request):
    return HttpResponse("You are at the event index")

@csrf_exempt
def create(request):
    if(request.method == 'POST'):
        data = json.loads(request.body) #Parse JSON data
        eventName = data.get('name')
        eventOrg = data.get('org')
        eventStartTime = data.get('start_time')
        eventEndTime = data.get('end_time')
        eventDate = data.get('date')
        eventLocation = data.get('location')
        eventBio = data.get('bio')
        
        message = ""
        date : datetime
        
        #Firstly see if the date was entered properly
        try:
            #Convert the string date to the date object (So queries are better)
            date = datetime.strptime(eventDate, '%m/%d/%Y')
        except ValueError:
            return JsonResponse({"Error": "Invalid format. Use MM/DD/YYYY"}, status=400)

        #Then convert the start and end times
        try:
            # Convert start_time and end_time
            startTime = datetime.strptime(eventStartTime, '%H:%M').time()
            endTime = datetime.strptime(eventEndTime, '%H:%M').time()
        except ValueError:
            return JsonResponse({"error": "Invalid time format. Please use HH:MM (24-hour format)."}, status=400)
        
        query = {"name": eventName, "org": eventOrg, "start_time": startTime, "end_time": endTime, "date": date, "location": eventLocation, "bio": eventBio}
        item_count = collection_name.count_documents(query)
        
        if(item_count != 0):
            message = "This event already exists"
            
        #Encrypt the password or something like that
        
        updated_data = {
                'name': eventName,
                'org': eventOrg,
                'start_time': startTime,
                'end_time': endTime,
                'date': date,
                'location': eventLocation,
                'bio': eventBio,
                'message': message
            }
        
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


@csrf_exempt
def getall(request):
    if(request.method == 'GET'):
        #Get the date from the get request
        stringDate = request.GET.get('date')
        if not stringDate:
            #Return error with an error code
            return JsonResponse({"error": "No date provided"}, status=400)
        try:
            #Try to convert the date to a date time object
            date = datetime.strptime(stringDate, '%m/%d/%Y')
        except ValueError:
            return JsonResponse({"Error": "Invalid format. Use MM/DD/YYYY"}, status=400)
        
        #Get the events in the database past the date (Or equal to)
        events = collection_name.find({
            "date": {
                "$gte": date
            }
        })
        event_list = list(events)
        #For now just update the total # of events and the event list
        updated_data = {
                'total': event_list.count(),
                'data': event_list,
            }
        return JsonResponse(updated_data)
        
    return HttpResponse("Only PUT requests are valid (Pretty Please)")

@csrf_exempt
def getusers(request):
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