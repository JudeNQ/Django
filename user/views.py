from django.db.models import F, Q
import re
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views import generic
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from bson.objectid import ObjectId

from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt

import json

# Connect to MongoDB server
uri = "mongodb+srv://cvmccoy123:testtest@cluster0.1tvfg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))
dbname = client['testData']
collection_name = dbname['users']


def index(request):
    return JsonResponse({"message": "Hello, world. You're at the user index."})


@csrf_exempt
@api_view(['POST'])
def create(request):
    """
    Handles user registration using REST API and MongoDB.
    """
    data = json.loads(request.body)
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    email_pattern = r'^(\w)+@my.unt.edu$'

    # Check email validity
    if not re.match(email_pattern, email):
        return JsonResponse({"error": "Invalid email. Use a @my.unt.edu email address"}, status=400)

    # Check if email already exists
    if collection_name.count_documents({"email": email}) > 0:
        return JsonResponse({"error": "This email is already in use"}, status=400)

    # Hash the password
    hashed_password = make_password(password)

    # Check if username already exists
    if collection_name.count_documents({"username": username}) > 0:
        return JsonResponse({"error": "Username already taken"}, status=400)

    # Insert user into MongoDB
    user_data = {
        "username": username,
        "email": email,
        "password": hashed_password,
    }
    try:
        result = collection_name.insert_one(user_data)
        user_data["_id"] = str(result.inserted_id)
        return JsonResponse(user_data, status=201)
    except Exception as e:
        return JsonResponse({"error": f"Failed to register user: {str(e)}"}, status=500)


@csrf_exempt
@api_view(['POST'])
def login_view(request):
    """
    Handles user login using REST API and MongoDB.
    """
    data = json.loads(request.body)
    email = data.get('email')
    password = data.get('password')

    # Retrieve user from MongoDB
    user = collection_name.find_one({"email": email})
    if not user or not make_password(password) == user['password']:
        return JsonResponse({"error": "Invalid email or password"}, status=400)

    return JsonResponse({
        "message": "Login successful",
        "username": user["username"],
        "email": user["email"]
    })


@csrf_exempt
@api_view(['POST'])
def profile_view(request):
    """
    View and update user profile.
    """
    data = json.loads(request.body)
    user_id = request.data.get("user_id")  # User should send their user_id in the body
    updates = {}

    # Handle profile updates (username, icon, location)
    if "username" in data:
        updates["username"] = data["username"]
    if "icon" in request.FILES:
        icon_file = request.FILES['icon']
        updates["icon"] = ContentFile(icon_file.read())

    if updates:
        try:
            collection_name.update_one({"_id": ObjectId(user_id)}, {"$set": updates})
            return JsonResponse({'message': 'Profile updated successfully!'})
        except Exception as e:
            return JsonResponse({'error': f"Failed to update profile: {str(e)}"}, status=500)
    else:
        # Fetch the profile
        profile = collection_name.find_one({"_id": ObjectId(user_id)})
        if profile:
            return JsonResponse({
                'username': profile.get('username'),
                'icon': profile.get('icon', 'default_icon.png'),
                'location': profile.get('location', ''),
            })
        return JsonResponse({'error': 'Profile not found'}, status=404)


@csrf_exempt
@api_view(['POST'])
def password_reset_request(request):
    """
    Handles password reset requests.
    """
    data = json.loads(request.body)
    email = data.get('email')

    user = collection_name.find_one({"email": email})
    if not user:
        return JsonResponse({'error': 'User not found'}, status=404)

    # Generate token and UID
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user['_id']))

    # Send password reset email
    reset_url = f"{settings.FRONTEND_URL}/reset/{uid}/{token}/"
    send_mail(
        subject="Password Reset Request",
        message=f"Click the link to reset your password: {reset_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email]
    )
    return JsonResponse({'message': 'Password reset email sent'})


@csrf_exempt
@api_view(['POST'])
def password_reset_confirm(request, uidb64, token):
    """
    Handles password reset confirmation.
    """
    data = json.loads(request.body)
    new_password = data.get('new_password')

    try:
        user_id = urlsafe_base64_decode(uidb64).decode()
        user = collection_name.find_one({"_id": ObjectId(user_id)})

        if user and default_token_generator.check_token(user, token):
            hashed_password = make_password(new_password)
            collection_name.update_one({"_id": ObjectId(user_id)}, {"$set": {"password": hashed_password}})
            return JsonResponse({'message': 'Password updated successfully'})
        return JsonResponse({'error': 'Invalid token or user ID'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f"Error resetting password: {str(e)}"}, status=500)
