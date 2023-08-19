from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from .models import Timesheet
from .forms import ClockingForm
from datetime import datetime, date

# Create your views here.
def clock_action(request):
    form = ClockingForm()  # Define default form
    error_message = None
    
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
                        error_message = f"{user.first_name} {user.last_name} have already clocked in today."
                        logout(request)
                    else:
                        # Perform clock in action
                        timesheet.logging = "IN"
                        timesheet.save()
                        logout(request)
                        return HttpResponse(f"{timesheet.employee} clocked in at {timesheet.clocking_time}")
                elif logging == "OUT":
                    # Check if the user has already clocked out
                    today = date.today()
                    existing_timesheet = Timesheet.objects.filter(employee=user, logging="OUT", clocking_time__date=today).first()
                    if existing_timesheet:
                        error_message = f"{user.first_name} {user.last_name} have already clocked out today."
                        logout(request)
                    else:
                        # Perform clock out action
                        timesheet.logging = "OUT"
                        timesheet.save()
                        logout(request)
                        return HttpResponseRedirect('/timesheet_success/out/?time=%s' % timesheet.clocking_time)
                else:
                    error_message = "Invalid logging value.\n"
            else:
                error_message = "Invalid form data.\n"
        else:
            error_message = "Invalid username or password.\n"
    
    context = {'error_message': error_message, 'form': form}
    return render(request, "index.html", context)


def timesheet_success(request, in_or_out): # Define function, accept a request and in_or_out
    """ displays to the employee the date and time that they logged in or out """

    timestamp = request.GET.get('time','Error')

    return render("timesheet_success.html", {'in_or_out':in_or_out, 'timestamp':timestamp}, context_instance=RequestContext(request))