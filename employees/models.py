from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _

class Business(models.Model):
	""" Business model """
	name = models.CharField(max_length=1024)

class JobRole(models.Model):
	""" JobRole model """
	title = models.CharField(max_length=1024)

class EmployeeProfile(models.Model):
    """ Employee model """
    GENDER_CHOICES = (('M', _('Male')), ('F', _('Female')))
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.IntegerField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES,blank=True, null=True)
    job_role = models.ForeignKey(JobRole,on_delete=models.CASCADE, blank=True, null=True)
    line_manager = models.ForeignKey(User,on_delete=models.CASCADE, blank=True, null=True,related_name="%(app_label)s_%(class)s_line_manager")
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(null=True, blank=True)
   
    def __str__(self):
        return self.user.first_name + " " + self.user.last_name


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a matching profile whenever a User is created."""
    if created:
        EmployeeProfile.objects.create(user=instance)


class Timesheet(models.Model):
    """ Timesheet model """
    LOGGING_CHOICES = (('IN', _('In')), ('OUT', _('Out')))
    # employee who recorded
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_employee")
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_recorded_by")   
    recorded_datetime = models.DateTimeField(auto_now_add=True)
    clocking_time = models.DateTimeField()
    # whether the user has clocked in or out
    logging = models.CharField(max_length=3, choices=LOGGING_CHOICES)
    ip_address = models.GenericIPAddressField()
    comments = models.TextField(blank=True, null=True)

    class Meta:
        get_latest_by = 'clocking_time'

    def __unicode__(self):
        return "%s checked %s at %s" % (self.employee, self.logging, self.clocking_time)


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


class SickLeave(models.Model):
    """ Sick timesheet model """
    employee  = models.ForeignKey(User, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_employee")
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_recorded_by")   
    recorded_datetime = models.DateTimeField(auto_now_add=True)
    date_from = models.DateTimeField()
    date_to = models.DateTimeField()
    doctors_note_provided = models.BooleanField()
    comments = models.TextField(blank=True, null=True)
