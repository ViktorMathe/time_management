from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import RegisterBusinessForm, ManagerProfileForm
from .models import ManagerProfile
from employees.models import EmployeeProfile, AnnualLeave
from clocking.models import Timesheet
from django.contrib.auth.decorators import login_required

# Create your views here.
def business_register(request):
    form = RegisterBusinessForm()
    if request.method == "POST":
        form = RegisterBusinessForm(request.POST)
        if form.is_valid():
           form.save(request)
           logout(request)
           return redirect('home')
        else:
           form = RegisterBusinessForm()

    context = {'form':form}
    return render(request, "reg_business.html", context)


@login_required
def manager_site(request):
    manager = get_object_or_404(ManagerProfile, user=request.user)
    all_employee = EmployeeProfile.objects.all()
    employees = all_employee.filter(company=manager.company)
    if request.method == 'POST':
        form = ManagerProfileForm(request.POST, instance=manager)
        print(form)
        if form.is_valid():
            form.save()
    else:
        form = ManagerProfileForm(instance=manager)
    
    template = 'manager.html'
    context = {
        'form': form,
        'employees': employees,
    }
    return render(request, template, context)


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
    """ Managemnent login is required. Enables the manager to view and edit employees timesheets and holidays requests"""
    # ORM queries the database for all of the entries.
    timesheets = Timesheet.objects.all() 
    holiday_requests = AnnualLeave.objects.all()

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
