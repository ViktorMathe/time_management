from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.shortcuts import render, get_object_or_404, redirect
from django.template import Context
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.template.context_processors import csrf
from django.contrib.auth.decorators import login_required
from .models import Timesheet, AnnualLeave, SickLeave, EmployeeProfile
from .forms import ClockingForm

from datetime import datetime, date
from django.utils.timezone import utc

"""
def clock_action(request): # Define function, accept a request and user details


    Receives the users input e.g. clock in / out actions, stores and retrieves records to and from the database
    # When the employee clocks in/out the post is received, the date and time is recorded and it is logged to the employees user_id
    clock_action = request.POST.get('clock_action','')  
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    logged_status = Timesheet.objects.filter(employee=user).latest()
    # when the employee logs in they can not log in again until they logout first 
    if clock_action == "ClockIn":
        if logged_status.logging == "OUT":
            timesheet = Timesheet(employee=user, recorded_by=user, clocking_time=now, logging="IN", ip_address=request.META.get('REMOTE_ADDR','NA'))
            timesheet.save()
            return HttpResponseRedirect('/timesheet_success/in/?time=%s' % now)
        else:
            error_message = "You must clock out before you can clock in.\n"
    # when the employee logs out they can not log out again until they login first
    elif clock_action == "ClockOut":
        if logged_status.logging == "IN":
            delta = now - logged_status.clocking_time
            hours = delta.total_seconds() / 3600.
            max_hours = 12
            # the employee cannot clock out more than 12 hours after the previous clock in
            if hours < max_hours:            
                timesheet = Timesheet(employee=user, recorded_by=user, clocking_time=now, logging="OUT", ip_address=request.META.get('REMOTE_ADDR','NA'))
                timesheet.save()
                return HttpResponseRedirect('/timesheet_success/out/?time=%s' % now)
            else:
                error_message = "You cannot clock out more than %s hours after previous clock in. Please report to manager.\n" % max_hours        
        else:
            error_message = "You must clock in before you can clock out.\n"        
    else:
        error_message = "Massive Error.\n"
    # errors are displayed if conditions are not satisfied

    context = {
        'error_message':error_message
    }
    return render(request, "index.html", context)
 
 

def clock_action(request):
    if request.method == 'POST':
        # Retrieve the logged-in user
        if request.user.is_authenticated:
           employee = request.user

        # Get the current datetime
           now = datetime.now()

        # Check if the employee has a corresponding timesheet entry for the current date
           timesheet_entry = Timesheet.objects.filter(employee=employee, recorded_datetime__date=now.date()).first()

        # Create a new timesheet entry if it doesn't exist
           if not timesheet_entry:
               timesheet_entry = Timesheet(employee=employee, recorded_datetime=now)

        # Set the appropriate time field based on the clock action
           if 'clock_in' in request.POST:
               timesheet_entry.clock_in = now.time()
               timesheet_entry.save()
               return HttpResponseRedirect(f'/timesheet_success/in/?time={now.strftime("%Y-%m-%d %H:%M:%S")}')
           elif 'clock_out' in request.POST:
               timesheet_entry.clock_out = now.time()
               timesheet_entry.save()
               return HttpResponseRedirect(f'/timesheet_success/out/?time={now.strftime("%Y-%m-%d %H:%M:%S")}')
        else:
            return render(request, "accounts/login.html")
    
    return render(request, 'index.html')
    """


def clock_action(request):
    if request.method == 'POST':
        form = ClockingForm(request.POST)
        if form.is_valid():
            logging_choice = form.cleaned_data['logging']
            timesheet_entry = Timesheet(logging=logging_choice)
            timesheet_entry.save()
            print("Timesheet entry saved:", timesheet_entry)
            return redirect('success')  # Replace 'success' with the URL name of your success page
        else:
            print("Form is not valid:", form.errors)
    else:
        form = ClockingForm()
    return render(request, 'clock.html', {'form': form})

@login_required
def clocking_view(request):
    if request.method == 'POST':
        form = ClockingForm(request.POST)
        if form.is_valid():
            timesheet = form.save(commit=False)
            timesheet.employee = request.user
            timesheet.recorded_by = request.user
            timesheet.clocking_time = datetime.now()
            timesheet.save()
            return redirect('success_page')
    else:
        form = ClockingForm()
    return render(request, 'clock.html', {'form': form})


def holiday_request(request, user):
    """ Takes the date and time that the employee requested from / to """ 
    holiday_request = request.POST.get('holiday_request','')
    if holiday_request == "HolidayRequest":
        holiday_req = AnnualLeave(employee=user, recorded_by=user, status=1)
        date_from = request.POST.get('date_from')
        time_from = request.POST.get('time_from')
        date_to = request.POST.get('date_to')
        time_to = request.POST.get('time_to')
        holiday_req.date_from = "%s %s" % (date_from, time_from)
        holiday_req.date_to = "%s %s" % (date_to, time_to)
        holiday_req.save()
        # displays a pending message to the employeee
        return HttpResponseRedirect('/vacation_pending/?datetimefrom=%s&datetimeto=%s' % (holiday_req.date_from, holiday_req.date_to))
    else:
        # error is displayed if conditions are not satisfied
        error_message = "Incorrect Holiday Request Action.\n"

        context = {'error_message':error_message}
        return render(request, "index.html", context)

"""
def clock_action(request):
    # Authenticate the user
    user = authenticate(request, username=request.user.username, password=request.POST.get('password'))
    
    if user is not None:
        print(user)
        form = ClockingForm(request.POST)
        if form.is_valid():
            timesheet = form.save(commit=False)
            print(timesheet)
            timesheet.employee = request.user
            print(timesheet.employee)
            timesheet.recorded_by = request.user
            timesheet.clocking_time = datetime.now()

            # Check if it's a clock in or clock out action
            clock_action = request.POST.get('clock_action', '')
            print(clock_action)
            
            if clock_action == "ClockIn":
                # Perform clock in action
                timesheet.logging = "IN"
                timesheet.save()
                return HttpResponseRedirect('/timesheet_success/in/?time=%s' % timesheet.clocking_time)
            elif clock_action == "ClockOut":
                # Perform clock out action
                timesheet.logging = "OUT"
                timesheet.save()
                return HttpResponseRedirect('/timesheet_success/out/?time=%s' % timesheet.clocking_time)
            else:
                error_message = "Invalid clock action.\n"
                print(1)
        else:
            error_message = "Invalid form data.\n"
            print(form.errors)
            print(2)
    else:
        error_message = "Invalid username or password.\n"
        print(3)
        
    context = {'error_message': error_message, 'form': form}
    return render(request, "index.html", context)

    """

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
                        error_message = "You have already clocked in today."
                    else:
                        # Perform clock in action
                        timesheet.logging = "IN"
                        timesheet.save()
                        return HttpResponseRedirect('/timesheet_success/in/?time=%s' % timesheet.clocking_time)
                elif logging == "OUT":
                    # Check if the user has already clocked out
                    today = date.today()
                    existing_timesheet = Timesheet.objects.filter(employee=user, logging="OUT", clocking_time__date=today).first()
                    if existing_timesheet:
                        error_message = "You have already clocked out today."
                    else:
                        # Perform clock out action
                        timesheet.logging = "OUT"
                        timesheet.save()
                        return HttpResponseRedirect('/timesheet_success/out/?time=%s' % timesheet.clocking_time)
                else:
                    error_message = "Invalid logging value.\n"
            else:
                error_message = "Invalid form data.\n"
        else:
            error_message = "Invalid username or password.\n"
    
    context = {'error_message': error_message, 'form': form}
    return render(request, "index.html", context)


def index(request):
    error_message = ""
    if request.method == "POST":
            # authenticate the user
            username = request.POST.get('employee_id','')
            password = request.POST.get('password','')
            # if empty an error message is displayed 
            if User is not None:
                # if its a clock in/out action or holiday request action its processed 
                if 'clock_action' in request.POST:
                    return clock_action(request)
                elif 'holiday_request' in request.POST:
                    return holiday_request(request,User)                   
            else:
                error_message = "Incorrect Username/Password.\n"
            
    context = {
        'error_message': error_message}
    # error is displayed if conditions are not satisfied
    return render(request, "index.html", context)

def timesheet_success(request, in_or_out): # Define function, accept a request and in_or_out
    """ displays to the employee the date and time that they logged in or out """

    timestamp = request.GET.get('time','Error')

    return render("timesheet_success.html", {'in_or_out':in_or_out, 'timestamp':timestamp}, context_instance=RequestContext(request))

def vacation_pending(request):
    """ displays to the employee the dates and times that they requested holidays form / to  """

    date_time_from = request.GET.get('datetimefrom','Error')
    
    date_time_to = request.GET.get('datetimeto','Error')

    return render("vacation_pending.html", {'date_time_from':date_time_from, 'date_time_to':date_time_to,}, context_instance=RequestContext(request))    


@login_required
def holiday_request_action(request, action, holiday_request_id): # Define function, accept a request, action and holiday_request_id
    """ Managemnent login is required. Enables the manager to approve, reject and cancel holiday requests """
    if action == "approve":
        annual_leave = AnnualLeave.objects.get(id=holiday_request_id)
        annual_leave.status = 2
        annual_leave.save()
        return HttpResponseRedirect('/loggedin/')
    elif action == "reject":                    
        annual_leave = AnnualLeave.objects.get(id=holiday_request_id)
        annual_leave.status = 3
        annual_leave.save()
        return HttpResponseRedirect('/loggedin/')
    elif action == "cancel":                    
        annual_leave = AnnualLeave.objects.get(id=holiday_request_id)
        annual_leave.status = 4
        annual_leave.save()
        return HttpResponseRedirect('/loggedin/')
    else:
        # display error massage
        error_message = "Incorrect Holiday Request Action.\n"
        return render("loggedin.html", {'error_message':error_message}, context_instance=RequestContext(request))


@login_required
def mgnt_clocking(request): #Define function, accept a request 
    """ Managemnent login is required. Enables the manager to clock in/out an employee """
    if request.method == "POST":
        # the employees id, and the managers clock action in/out 
        username = request.POST.get('employee_id', '')        
        mgnt_clock_action = request.POST.get('mgnt_clock_action','')
        # 
        try:
            employee = User.objects.get(username=username)

            if mgnt_clock_action == "ClockIn":
                clockin_date = request.POST.get('clockin_date')
                clockin_time = request.POST.get('clockin_time')
                # create Timesheet with logging = IN, time = now
                timesheet = Timesheet(employee=employee, recorded_by=request.user, logging="IN", ip_address=request.META.get('REMOTE_ADDR','NA'))
                timesheet.clocking_time = "%s %s" % (clockin_date, clockin_time)
                timesheet.save()
                return HttpResponseRedirect('/loggedin/')
            elif mgnt_clock_action == "ClockOut":
                clockin_date = request.POST.get('clockin_date')
                clockin_time = request.POST.get('clockin_time')
                # create Timesheet with logging = IN, time = now
                timesheet = Timesheet(employee=employee, recorded_by=request.user, logging="OUT", ip_address=request.META.get('REMOTE_ADDR','NA'))
                timesheet.clocking_time = "%s %s" % (clockin_date, clockin_time)
                timesheet.save()
                return HttpResponseRedirect('/loggedin/')
            else:
                error_message = "Incorrect Sick Leave Action.\n"
                return render("loggedin.html", {'error_message':error_message}, context_instance=RequestContext(request))
        except Exception as e:
            return render("loggedin.html", {'error_message':"%s"%e}, context_instance=RequestContext(request))
    else:        
        return HttpResponseRedirect('/loggedin/')

@login_required
def loggedin(request):  # Define function, accept a request 
    """ Managemnent login is required. Enables the manager to view and edit employees timesheets, holidays requests and sick leave """
    # ORM queries the database for all of the entries.
    timesheets = Timesheet.objects.all() 
    holiday_requests = AnnualLeave.objects.all()
    sick_leave = SickLeave.objects.all()

    error_message = ""
    context = {
        'error_message':error_message,
        'full_name':request.user.username,
        'timesheets': timesheets,
        'holiday_requests': holiday_requests,
        'sick_leave': sick_leave,
    }
    
    # Responds with passing the object items (contains info from the DB) to the template loggedin.html 
    return render(request, 'loggedin.html', context)