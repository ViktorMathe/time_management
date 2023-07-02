from django.contrib import admin
from datetime import timedelta 
from .models import Business, JobRole, EmployeeProfile, Timesheet, AnnualLeave, SickLeave

# Register your models here.
admin.site.register(Business)
admin.site.register(EmployeeProfile)

class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = (
        'first_name' + 'last_name',
    )

class TimesheetAdmin(admin.ModelAdmin):
    list_display = ('employee', 'clocking_time', 'logging', 'get_worked_hours')


        

admin.site.register(Timesheet, TimesheetAdmin)