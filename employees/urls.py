from django.urls import include, path
from . import views

urlpatterns = [
	path('vacation_pending/', views.vacation_pending),
	path('holiday_request/', views.holiday_request_action),
	path('profile/', views.employee_profile, name='profile'),
	path('timesheet/', views.view_timesheets, name='timesheets'),
	path('holidays/', views.holidays, name='holidays'),
	path('delete_profile/<id>', views.delete_profile, name='delete_profile')
]