from django.urls import include, path
from . import views

urlpatterns = [
    path('timesheet_success/', views.timesheet_success),
]