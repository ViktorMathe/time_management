from django.urls import include, path
from . import views

urlpatterns = [
	path('', views.index, name='home'),
	path('timesheet_success/', views.timesheet_success),
	path('vacation_pending/', views.vacation_pending),
	path('sick_leave/', views.sick_leave),
	path('mgnt_clocking/', views.mgnt_clocking),
	path('holiday_request/', views.holiday_request_action),
	path('loggedin/', views.loggedin),
	path('clocking/', views.clocking_view, name='clocking'),
]