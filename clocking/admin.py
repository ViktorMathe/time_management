from django.contrib import admin
from .models import Timesheet

# Register your models here.
class TimesheetAdmin(admin.ModelAdmin):
    list_display = ('get_employee_name', 'clocking_time', 'logging', 'get_worked_hours', 'get_weekly_hours', 'get_monthly_hours')

admin.site.register(Timesheet, TimesheetAdmin)