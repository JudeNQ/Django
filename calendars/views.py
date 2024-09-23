from django.db.models import F
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
import pymongo
from django.conf import settings


# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You're at the calendar index.")

'''
connect_string = 'mongodb+srv://cvmccoy123:<testingtesting>@cluster0.1tvfg.mongodb.net/' 
my_client = pymongo.MongoClient(connect_string)

# First define the database name
dbname = my_client['sample_users']

# Now get/create collection name (remember that you will see the database in your mongodb cluster only after you create a collection
collection_name = dbname["userdetails"]

#let's create two documents
user_1 = {
    "user_id": "RR000123456",
    "common_name" : "John",
    "scientific_name" : "Johnus",
    "available" : "Y",
    "category": "Sophomore"
}
user_2 = {
    "user_id": "RR000342522",
    "common_name" : "Jessica",
    "scientific_name" : "Jessicus",
    "available" : "Y",
    "category" : "Junior"
}
# Insert the documents
collection_name.insert_many([user_1,user_2])
# Check the count
count = collection_name.count()
print(count)

# Read the documents
med_details = collection_name.find({})
# Print on the terminal
for r in med_details:
    print(r["common_name"])
# Update one document
#update_data = collection_name.update_one({'medicine_id':'RR000123456'}, {'$set':{'common_name':'Paracetamol 500'}})

# Delete one document
#delete_data = collection_name.delete_one({'medicine_id':'RR000123456'})
'''