from django.contrib import admin
from datetime import timedelta 
from .models import Business, JobRole, EmployeeProfile, Timesheet, AnnualLeave

# Register your models here.
admin.site.register(Business)
admin.site.register(EmployeeProfile)

class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = (
        'first_name' + 'last_name',
    )

class TimesheetAdmin(admin.ModelAdmin):
    list_display = ('get_employee_name', 'clocking_time', 'logging', 'get_worked_hours', 'get_weekly_hours', 'get_monthly_hours')


        

admin.site.register(Timesheet, TimesheetAdmin)