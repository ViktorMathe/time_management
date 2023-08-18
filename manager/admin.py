from django.contrib import admin
from .models import Business, ManagerProfile


# Register your models here.
class BusinessAdminSite(admin.ModelAdmin):
    list_display=('business_name', 'get_manager_first_name', 'get_manager_last_name', 'view_employees')
    
    def view_employees(self, obj):
        employees = EmployeeProfile.objects.filter(company=obj)
        return ", ".join([f"{employee.user.first_name} {employee.user.last_name}" for employee in employees])

    view_employees.short_description = 'Employees'
    view_employees.admin_order_field = 'employeeprofile'

    def get_queryset(self, request):
        # Restrict the queryset to businesses where the current user is the manager
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(manager=request.user)
        return qs

    def get_manager_first_name(self, obj):
        return obj.manager.first_name

    def get_manager_last_name(self, obj):
        return obj.manager.last_name

    get_manager_first_name.short_description = 'Manager First Name'
    get_manager_last_name.short_description = 'Manager Last Name'

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj=obj) or ()
        if obj:
            # Make the 'manager' field read-only when editing an existing Business
            readonly_fields += ('manager',)
        return readonly_fields

admin.site.register(Business, BusinessAdminSite)


class ManagerProfileAdmin(admin.ModelAdmin):
    list_display = ('get_manager_first_name', 'get_manager_last_name', 'get_manager_company')

    def get_manager_first_name(self, obj):
        return obj.user.first_name

    def get_manager_last_name(self, obj):
        return obj.user.last_name

    def get_manager_company(self, obj):
        return obj.company

    get_manager_first_name.short_description = 'Manager First Name'
    get_manager_last_name.short_description = 'Manager Last Name'

admin.site.register(ManagerProfile, ManagerProfileAdmin)