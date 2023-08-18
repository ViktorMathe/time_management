from django.urls import include, path
from . import views

urlpatterns = [
	path('', views.index, name='home'),
	path('reg_business/', views.business_register, name='business_reg'),
	path('timesheet_success/', views.timesheet_success),
	path('vacation_pending/', views.vacation_pending),
	path('mgnt_clocking/', views.mgnt_clocking),
	path('holiday_request/', views.holiday_request_action),
	path('loggedin/', views.loggedin),
	path('profile/', views.employee_profile, name='profile'),
	path('manager/', views.manager_site, name='manager'),
]