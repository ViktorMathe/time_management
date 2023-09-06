from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from .models import Timesheet
from .forms import ClockingForm
from datetime import datetime, date
from django.contrib import messages

# Create your views here.
def clock_action(request):
    form = ClockingForm()  # Define default form
    
    if request.method == 'POST':
        # Retrieve form data
        employee_id = request.POST.get('employee_id')
        password = request.POST.get('password')
        logging = request.POST.get('logging')
        
        # Authenticate the user
        user = authenticate(request, username=request.user.username, password=password)
        
        if user is not None:
            form = ClockingForm(request.POST)
            
            if form.is_valid():
                timesheet = form.save(commit=False)
                timesheet.employee = user
                timesheet.recorded_by = user
                timesheet.clocking_time = datetime.now()

                if logging == "IN":
                    # Check if the user has already clocked in
                    today = date.today()
                    existing_timesheet = Timesheet.objects.filter(employee=user, logging="IN", clocking_time__date=today).first()
                    if existing_timesheet:
                        messages.error(request, f"{user.first_name} {user.last_name} have already clocked in today.")
                        logout(request)
                    else:
                        # Perform clock in action
                        timesheet.logging = "IN"
                        timesheet.save()
                        logout(request)
                        messages.success(request, f"{timesheet.employee} clocked in at {timesheet.clocking_time.replace(microsecond=0)}")
                        return redirect('home')
                elif logging == "OUT":
                    # Check if the user has already clocked out
                    today = date.today()
                    existing_timesheet = Timesheet.objects.filter(employee=user, logging="OUT", clocking_time__date=today).first()
                    if existing_timesheet:
                        messages.error(request, f"{user.first_name} {user.last_name} have already clocked out today.")
                        logout(request)
                    else:
                        # Perform clock out action
                        timesheet.logging = "OUT"
                        timesheet.save()
                        logout(request)
                        messages.success(request, f"{timesheet.employee} clocked out at {timesheet.clocking_time.replace(microsecond=0)}")
                        return redirect('home')
                else:
                    messages.error(request, "Invalid logging value.")
            else:
                messages.error(request, "Invalid form data.")
        else:
            messages.error(request, "Invalid username or password.")
    
    context = {'form': form}
    return render(request, "index.html", context)
