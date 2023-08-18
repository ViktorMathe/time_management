from django.contrib import admin 
from .models import JobRole, EmployeeProfile, AnnualLeave


class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = (
        'get_employee_first_name', 'get_employee_last_name', 'get_employee_company'
    )

    def get_employee_first_name(self, obj):
        return obj.user.first_name

    def get_employee_last_name(self, obj):
        return obj.user.last_name

    def get_employee_company(self, obj):
        return obj.company

    get_employee_first_name.short_description = 'Employee First Name'
    get_employee_last_name.short_description = 'Employee Last Name'
    get_employee_company.short_description = 'Company'

    get_employee_company.admin_order_field = 'company__business_name'

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj=obj) or ()
        if obj:
            # Make the 'company' field read-only when editing an existing EmployeeProfile
            readonly_fields += ('company',)
        return readonly_fields

admin.site.register(EmployeeProfile, EmployeeProfileAdmin)

admin.site.register(JobRole)