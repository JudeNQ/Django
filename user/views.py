import re
from django.db.models import F
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from django.conf import settings

import json
from django.http import JsonResponse

from rest_framework import generics
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
            
        #Encrypt the password or something like that
        
        updated_data = {
                'email': email,
                'password': password,  #Encrypted password (or no password)
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