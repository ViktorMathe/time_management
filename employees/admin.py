from django.contrib import admin
from .models import Business, JobRole, EmployeeProfile, Timesheet, AnnualLeave, SickLeave

# Register your models here.
admin.site.register(Business)
admin.site.register(EmployeeProfile)
admin.site.register(Timesheet)

class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = (
        'first_name' + 'last_name',
    )