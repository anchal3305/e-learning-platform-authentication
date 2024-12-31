from django.shortcuts import render, redirect
from django.contrib import messages
from auth_project.db_connection import db
from pymongo.errors import DuplicateKeyError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from bson import ObjectId
from django.http import JsonResponse

# MongoDB users collection
users_collection = db['users']

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validate form data
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'auth/register.html', {})

        try:
            # Save user in MongoDB
            users_collection.insert_one({
                "username": username,
                "password": generate_password_hash(password1),  # Hash passwords for security
                "is_active": True,
                "date_joined": str(datetime.now())
            })
            messages.success(request, "Registration successful. Please log in.")
            return redirect('login')
        except DuplicateKeyError:
            messages.error(request, "Username already exists.")
            return render(request, 'auth/register.html', {})

    return render(request, 'auth/register.html', {})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = users_collection.find_one({"username": username})  # Hash password check here
        if user and check_password_hash(user['password'], password):
            # Simulate Django login by saving user ID in the session
            request.session['user_id'] = str(user['_id'])
            messages.success(request, "Login successful.")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'auth/login.html')

    return render(request, 'auth/login.html', {})  # Render empty form

def dashboard_view(request):
    # Retrieve user data from MongoDB
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')  # Redirect if user_id is not in session
    
    try:
        user_data = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user_data:
            messages.error(request, "User not found.")
            return redirect('login')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('login')

    return render(request, 'dashboard.html', {"user_data": user_data})

def logout_view(request):
    # Simulate Django logout by clearing session
    request.session.flush()
    messages.success(request, "Logged out successfully.")
    return redirect('login')