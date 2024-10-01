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

#Connect to the server
uri = "mongodb+srv://cvmccoy123:testtest@cluster0.1tvfg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

def index(request):
    return HttpResponse("Hello, world. You're at the user index.")

def create(request):
    print("Someone visit create")
    if(request.method == 'POST'):
        data = json.loads(request.body) #Parse JSON data
        dbname = client['testData']
        collection_name = dbname["users"]
        medicine_1 = {
            "medicine_id": data,
            "common_name" : "Paracetamol",
            "scientific_name" : "",
            "available" : "Y",
            "category": "fever"
        }
        print(data)
        #collection_name.insert_one()
        return JsonResponse(data)
    return HttpResponse("You're creating a user")