from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from clocking.views import clock_action
from manager.views import business_register

# Create your views here.
def index(request):
    if request.method == "POST":
        # Retrieve form data
        employee_id = request.POST.get('employee_id', '')
        password = request.POST.get('password', '')
        
        # Authenticate the user
        user = authenticate(request, username=employee_id, password=password)
        
        if user is not None:
            login(request, user)  # Log in the authenticated user
            if 'clock_action' in request.POST:
                return clock_action(request)
            else:
                logout(request)  # Log out the user after form submission
                return redirect('home')  # Redirect to the homepage or any other desired page
        else:
            messages.error(request, "Incorrect Username/Password.")

    return render(request, "index.html")