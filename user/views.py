from django.db.models import F, Q
import re
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from django.conf import settings
#from .models import Schedule, Event
#from .forms import UserCompareForm, ScheduleCompareForm, EventCompareForm


import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login

from rest_framework import generics
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from bson.objectid import ObjectId

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
        name = data.get('name')
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
        
        '''
        # Check if the user already exists (optional but recommended)
        if User.objects.filter(name=name).exists():
            return JsonResponse({'error': 'Username already taken'}, status=400)
        
        # Create a new user instance
        user = User(name=name, email=email, password=hashed_password)
        user.save()  # Save the user to the database
        '''

        # Omit the raw password in the response for security reasons
        updated_data = {
            'name': name,
            'email': email,
            'password': password,  #Encrypted password (or no password)
            'message': message
            # Do not return or print the raw password for security reasons
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
    # If the request method is not POST, return an error response
    return JsonResponse({'error': 'Only POST requests are valid'}, status=400)



@csrf_exempt
def createschedule(request):
    if(request.method == 'POST'):
        data = json.loads(request.body) #Parse JSON data
        userRawId = data.get('_id')
        schedule = data.get('Schedule')
        
        try:
            userId = ObjectId(userRawId)
        except Exception as e:
            return JsonResponse({'Error' : "Invalid ID format"}, status=404)
        
        #Get the user with the given Id
        queryUser = {'_id' : userId}
        
        #try to get user from database
        user = collection_name.find_one(queryUser)
        
        #If the user doesn't exist
        if not user:
            return JsonResponse({'Error': "No user exists with that ID"}, status=404)
        
        #Attempt to insert the user data into the mongo_db database
        try:
            #Add the schedule to the users model
            collection_name.update_one(
                {"_id": userId},
                {"$set": {"schedule": schedule}},
                upsert=True
            )
            return JsonResponse({"message": "Schedule saved successfully!"}, status=200)
        except Exception as e:
            print(f"Error inserting data: {e}")
            return JsonResponse({"error": str(e)}, status=500)
    # If the request method is not POST, return an error response
    return JsonResponse({'error': 'Only POST requests are valid'}, status=400)

        
@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)  # Parse JSON data

        # Get the email, username, and password from the JSON data
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        # Authenticate the user using Django's built-in authenticate function
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # If the user is authenticated, log them in and start a session
            login(request, user)

            # Return a success response in JSON format
            return JsonResponse({'message': 'Login successful!', 'username': username})
        else:
            # Check MongoDB if Django authentication fails or to verify extra information
            query = {"email": email, "password": password}  # You should hash the password before storing/checking
            item_count = collection_name.count_documents(query)
            user = collection_name.find_one(query)
            

            # Handle MongoDB results
            if item_count != 0:
                updated_data = {
                    'email': email,
                    'password': password,  # Ideally, store the hashed password here
                    'confirmed': "True",
                    'id': str(user['_id'])
                }
            else:
                updated_data = {
                    'email': email,
                    'password': password,  # Hashed password
                    'confirmed': "False"
                }

            try:
                # MongoDB insert code is commented out because you're not creating users in the login function
                # Uncomment if needed for user creation
                # result = collection_name.insert_one(updated_data)
                # Convert ObjectId to string (if you are creating users instead)
                # updated_data['_id'] = str(result.inserted_id)

                # Return the updated data based on MongoDB verification
                return JsonResponse(updated_data)

            except Exception as e:
                print(f"Error inserting data: {e}")
                return JsonResponse({"error": str(e)}, status=500)

    # If the request method is not POST, return an error response
    return JsonResponse({'error': 'Only POST requests are valid'}, status=400)


'''
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

#password reset and confirmation email views
@csrf_exempt
@api_view(['POST'])
def password_reset_request(request):
    """
    Handle password reset requests.
    - Find the user by email in MongoDB.
    - Generate a token and UID for password reset.
    - Send a reset email with a reset URL.
    """
    data = json.loads(request.body)
    email = data.get('email')

    # Search for user by email in MongoDB
    user = collection_name.find_one({"email": email})

    if user:
        # Generate a token and base64 encode the user ID
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user['_id']))

        # Prepare password reset URL (for Android app to display)
        reset_url = f'http://your_frontend_url/reset/{uid}/{token}/'

        # Send the password reset email
        send_mail(
            subject="Password Reset Request",
            message=f'Use the following link to reset your password: {reset_url}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return JsonResponse({'message': 'Password reset email sent'}, status=200)
    else:
        return JsonResponse({'error': 'User not found'}, status=404)
    
@csrf_exempt
@api_view(['POST'])
def password_reset_confirm(request, uidb64, token):
    """
    Confirm password reset and update the user's password in MongoDB.
    - Decode user ID.
    - Validate the token and update password.
    """
    data = json.loads(request.body)
    new_password = data.get('new_password')

    try:
        # Decode the user's ID
        user_id = urlsafe_base64_decode(uidb64).decode()

        # Find the user in MongoDB
        user = collection_name.find_one({"_id": ObjectId(user_id)})

        if user and default_token_generator.check_token(user, token):
            # Hash the new password and update MongoDB
            hashed_password = make_password(new_password)
            collection_name.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"password": hashed_password}}
            )
            return JsonResponse({'message': 'Password has been reset'}, status=200)
        else:
            return JsonResponse({'error': 'Invalid token or user ID'}, status=400)

    except (TypeError, ValueError, OverflowError):
        return JsonResponse({'error': 'Invalid user ID'}, status=400)
    
# Function to send an account verification email
def send_verification_email(request, user):
    token_generator = default_token_generator
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))  # Encode the user's ID for use in the URL
    token = token_generator.make_token(user)  # Generate the unique token for the user

    # Create the email subject and message
    subject = "Verify your account - PlanIt"
    message = render_to_string('email_verification.html', {
        'user': user,
        'uidb64': uidb64,
        'token': token,
        'domain': request.get_host(),  # Get the current domain (used for the link)
    })

    # Send the email using Django's send_mail function
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,  # From email
        [user.email],  # To email (the user who is verifying their account)
        fail_silently=False,  # Raise an error if the email fails to send
        html_message=message  # Use the HTML template for the email body
    )

    # Return a JSON response indicating success
    return JsonResponse({
        "message": "Verification email sent to " + user.email,
        "email": user.email
    })

# View to verify the account after the user clicks the email link
def verify_account(request, uidb64, token):
    token_generator = default_token_generator
    try:
        # Decode the user ID from the URL
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Check if the token is valid for this user
    if user is not None and token_generator.check_token(user, token):
        # Activate the user (or set verified=True if using MongoDB)
        user.is_active = True
        user.save()
        # Return a JSON response on success
        return JsonResponse({
            "message": "Account successfully verified.",
            "user_id": user.id
        })
    else:
        # Return an error response if the token is invalid
        return JsonResponse({
            "error": "Invalid token or user.",
        }, status=400)
'''