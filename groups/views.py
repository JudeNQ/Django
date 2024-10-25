from bson import ObjectId
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
collection_name = dbname['groups']

def index(request):
    return HttpResponse("You are at the group index")

@csrf_exempt
def create(request):
    if(request.method == 'POST'):
        data = json.loads(request.body)
        #Parse the JSON data
        groupName = data.get('name')
        groupBio = data.get('bio')
        groupLeader = data.get('leader')
        
        #Convert the string ids to mongo Id's
        try:
            userId = ObjectId(groupLeader)
        except Exception as e:
            return JsonResponse({'message': 'Invalid ID format'}, status=400)
        
        userList = []
        userList.append(userId)
        
        updated_data = {
            'name': groupName,
            'bio': groupBio,
            'leader': groupLeader,
            'members': userList
        }
        
        #Attempt to insert the group data into the mongo_db database
        try:
            result = collection_name.insert_one(updated_data)  # Insert into MongoDB
            # Convert ObjectId to string
            updated_data['_id'] = str(result.inserted_id)
            return JsonResponse(updated_data)
        except Exception as e:
            print("Error inserting data: {e}")
            return JsonResponse({"error": str(e)}, status=500)
    return HttpResponse("Only PUT requests are valid (Pretty Please)")

#Gets a users saved groups. Won't do anything if the user doesn't have any saved groups... Yeah
@csrf_exempt
def getGroups(request):
    if(request.method == 'GET'):
        #Process the userId given with the GET request
        userID = request.GET.get('user')
        try:
            userId = ObjectId(userID)
        except Exception as e:
            return JsonResponse({'Error' : "Invalid ID format"})
        
        #Get the user with the given Id
        queryUser = {'_id' : userID}
        
        #try to get user from database
        user = dbname['users'].find_one(queryUser)
        
        #If the user doesn't exist
        if not user:
            return JsonResponse({'Error': "No user exists with that ID"}, status=404)
        
        #Search through all saved groups to find ones that the userID is apart of
        groups = []
        
        #Get all the groups from the database
        allGroups =collection_name.find()
        
        #Loop through each group
        for group in allGroups:
            members = group['members']
            #loop through each member thats part of the group
            for member in members:
                #If the memberID = userID then yippee (should change this in the future)
                if(member == userID):
                    groups.append(group)
                    break
        
        group_list = list(groups)
        #For now just update the total # of groups and the group list
        updated_data = {
                'total': group_list.count(),
                'data': group_list,
            }
        return JsonResponse(updated_data)
        
    return HttpResponse("Only GET requests are valid (Pretty Please)")