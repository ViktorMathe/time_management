from django.urls import include, path
from . import views

urlpatterns = [
	path('vacation_pending/', views.vacation_pending),
	path('holiday_request/', views.holiday_request_action),
	path('profile/', views.employee_profile, name='profile'),
]