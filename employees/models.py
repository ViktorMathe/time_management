from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from manager.models import ManagerProfile, Business


class JobRole(models.Model):
	""" JobRole model """
	title = models.CharField(max_length=1024)


class EmployeeProfile(models.Model):
    """ Employee model """
    GENDER_CHOICES = (('M', _('Male')), ('F', _('Female')))
    APPROVED = ((0,'Pending'), (1, 'Approved'))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.IntegerField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES,blank=True, null=True)
    job_role = models.ForeignKey(JobRole,on_delete=models.CASCADE, blank=True, null=True)
    line_manager = models.ForeignKey(ManagerProfile, on_delete=models.CASCADE, blank=True, null=True,related_name="%(app_label)s_%(class)s_line_manager")
    approved = models.BooleanField(choices=APPROVED, default=0)
    company = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True, null=True)
    start_date = models.DateField(default=None, blank=True, null=True)
    end_date = models.DateField(null=True, blank=True)
   
    def __str__(self):
        return self.user.first_name + " " + self.user.last_name

    def save(self, *args, **kwargs):
        # Set the start_date to the user's date_joined when it's not provided
        if not self.start_date and self.user:
            self.start_date = self.user.date_joined.date()
        super(EmployeeProfile, self).save(*args, **kwargs)


class AnnualLeave(models.Model):
    """ Vacation timesheet model """
    STATUS_CHOICES = ((1, _('Pending')), (2, _('Granted')), (3, _('Rejected')), (4, _('Cancelled')),)
    employee  = models.ForeignKey(User, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_employee")
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_recorded_by")   
    recorded_datetime = models.DateTimeField(auto_now_add=True)
	# status of the annual leave request pending, granted, rejected or cancelled
    status = models.IntegerField(_('status'), choices=STATUS_CHOICES)
    date_from = models.DateTimeField()
    date_to = models.DateTimeField()
    comments = models.TextField(max_length=500, blank=True, null=True)

