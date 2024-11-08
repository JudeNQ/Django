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
        password = data.get('password')
        
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
            'leader': userId,
            'members': userList,
            'password': password
        }
        
        #Attempt to insert the group data into the mongo_db database
        try:
            result = collection_name.insert_one(updated_data)  # Insert into MongoDB
            # Convert ObjectId to string
            updated_data['_id'] = str(result.inserted_id)
            updated_data['leader'] = groupLeader
            updated_data['members'] = [str(member) for member in updated_data['members']]
            return JsonResponse(updated_data)
        except Exception as e:
            print(f"Error inserting data: {e}")
            return JsonResponse({"error": str(e)}, status=500)
    return HttpResponse("Only POST requests are valid (Pretty Please)")

#Gets a users saved groups. Won't do anything if the user doesn't have any saved groups... Yeah
@csrf_exempt
def getGroups(request):
    #See if a user ID was specified
    if(request.method == 'GET'):
        #Process the userId given with the GET request
        if(request.GET.get('user')):
            userID = request.GET.get('user')
            try:
                userId = ObjectId(userID)
            except Exception as e:
                return JsonResponse({'Error' : "Invalid ID format"})
            
            #Search through all saved groups to find ones that the userID is apart of
            groups = []
            group_list = []
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
            
            for group in groups:
                #Convert the MongoID field to one that is readable by JSON
                group['_id'] = str(group['_id'])
                group['leader'] = str(group['leader'])
                group['members'] = [str(member) for member in group['members']]
                group_list.append(group)
                
            #For now just update the total # of groups and the group list
            updated_data = {
                    'total': len(group_list),
                    'data': group_list,
                }
            return JsonResponse(updated_data)
        else:
            allGroups = collection_name.find()
            group_list = []
            for group in allGroups:
                #Convert the MongoID field to one that is readable by JSON
                group['_id'] = str(group['_id'])
                group['leader'] = str(group['leader'])
                group['members'] = [str(member) for member in group['members']]
                group_list.append(group)
                
            updated_data = {
                'total': len(group_list),
                'data': group_list
            }
            return JsonResponse(updated_data)
        
    return HttpResponse("Only GET requests are valid (Pretty Please)")

#Joins a specific group.
#Takes in a JSON file with the group ID, UserID, and the password entered.
#Should return a message
@csrf_exempt
def join(request):
    if(request.method == 'POST'):
        #load the JSON file
        data = json.loads(request.body)
        #get the ids
        userID = data.get('user')
        groupID = data.get('group')
        password = data.get('password')
        try:
            userId = ObjectId(userID)
            groupId = ObjectId(groupID)
        except Exception as e:
            return JsonResponse({'Error' : "Invalid ID format"})
        
        #get the group based off the id
        group = collection_name.find_one(groupId)
        #make sure the password is good
        if(group['password'] != password):
            return JsonResponse({'Error' : "Invalid Password"})
        
        #now check to see if the user is already part of the group
        members = group.get('members', [])
        if userId in members:
            return JsonResponse({'Error': "User already in the group"}, status=409)
        
        #now that its all good insert the member into members
        members.append(userId)
        
        # Set the update operation
        update_operation = {'$set': {'members': members}}
        
        try:
            collection_name.update_one({'_id': groupId}, update_operation)
        except Exception as e:
            return JsonResponse({'Error': "Error joining group", 'Details': str(e)}, status=500)
        
        #For now just send the success message
        updated_data = {
                'message': "Joining group was successful"
            }
        return JsonResponse(updated_data)
        
    return HttpResponse("Only GET requests are valid (Pretty Please)")