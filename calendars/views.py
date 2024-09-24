from django.db.models import F
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from django.conf import settings


# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You're at the calendar index.")




uri = "mongodb+srv://cvmccoy123:testtest@cluster0.1tvfg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# First define the database name
dbname = client['testData']

# Now get/create collection name (remember that you will see the database in your mongodb cluster only after you create a collection
collection_name = dbname["users"]