from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from datetime import timedelta, date

class Business(models.Model):
    """ Business model """
    name = models.CharField(max_length=1024)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)


class JobRole(models.Model):
	""" JobRole model """
	title = models.CharField(max_length=1024)


class EmployeeProfile(models.Model):
    """ Employee model """
    GENDER_CHOICES = (('M', _('Male')), ('F', _('Female')))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.IntegerField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES,blank=True, null=True)
    job_role = models.ForeignKey(JobRole,on_delete=models.CASCADE, blank=True, null=True)
    line_manager = models.ForeignKey(User,on_delete=models.CASCADE, blank=True, null=True,related_name="%(app_label)s_%(class)s_line_manager")
    company = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True, null=True)
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
    company = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True, null=True)
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_recorded_by")   
    recorded_datetime = models.DateTimeField(auto_now_add=True)
    clocking_time = models.DateTimeField(null=True)
    # whether the user has clocked in or out
    logging = models.CharField(max_length=3, choices=LOGGING_CHOICES)
    ip_address = models.GenericIPAddressField(null=True)
    comments = models.TextField(blank=True, null=True)
    worked_hours = models.CharField(max_length=54, null=True)

    class Meta:
        get_latest_by = 'clocking_time'
        

    def worked_hours(self):
        if self.logging == 'OUT' and self.clocking_time and self.recorded_by_id:
            previous_in_timesheet = Timesheet.objects.filter(
                employee_id=self.employee_id,
                recorded_datetime__date=self.recorded_datetime.date(),
                logging='IN'
            ).exclude(id=self.id).order_by('recorded_datetime').last()

            if previous_in_timesheet:
                working_time = self.clocking_time - previous_in_timesheet.clocking_time
            else:
                working_time = timedelta()

                return str(working_time)
        else:
            return "Clock-out not recorded yet."

    def get_worked_hours(self):
        if self.logging == 'OUT':
            try:
                previous_timesheet = Timesheet.objects.filter(
                    employee=self.employee,
                    logging='IN',
                    recorded_datetime__lt=self.recorded_datetime
                ).latest('recorded_datetime')

                worked_time = self.recorded_datetime - previous_timesheet.recorded_datetime

                hours, remainder = divmod(worked_time.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)

                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            except Timesheet.DoesNotExist:
                return "Incomplete clocking data"

        return "Incomplete clocking data"
    
    def get_clocking_time_in(self):
        try:
            return Timesheet.objects.filter(
                employee=self.employee,
                logging='IN',
                recorded_datetime__lt=self.recorded_datetime
            ).latest('recorded_datetime').recorded_datetime
        except Timesheet.DoesNotExist:
            return None

    def format_hours_minutes(self, hours, minutes):
        return f"{int(hours):02}:{int(minutes):02}"

    def get_weekly_hours(self):
        # Get the start date of the week (Monday)
        week_start_date = self.clocking_time.date() - timedelta(days=self.clocking_time.weekday())

        # Calculate the end date of the week (Sunday)
        week_end_date = week_start_date + timedelta(days=6)

        # Filter timesheets for the employee and week range
        timesheets = Timesheet.objects.filter(
            employee=self.employee,
            logging='OUT',
            clocking_time__date__range=[week_start_date, week_end_date]
        )

        # Calculate total worked hours for the week
        total_hours = sum(
            (timesheet.clocking_time - timesheet.get_clocking_time_in()).total_seconds()
            for timesheet in timesheets
        )

        # Convert total seconds to hours and minutes
        total_minutes, _ = divmod(total_hours, 60)
        total_hours, minutes = divmod(total_minutes, 60)

        return self.format_hours_minutes(total_hours, minutes)

    def get_monthly_hours(self):
        # Get the start date of the month
        month_start_date = date(self.clocking_time.year, self.clocking_time.month, 1)

        # Calculate the end date of the month
        next_month = month_start_date.replace(day=28) + timedelta(days=4)
        month_end_date = next_month - timedelta(days=next_month.day)

        # Filter timesheets for the employee and month range
        timesheets = Timesheet.objects.filter(
            employee=self.employee,
            logging='OUT',
            clocking_time__date__range=[month_start_date, month_end_date]
        )

        # Calculate total worked hours for the month
        total_hours = sum(
            (timesheet.clocking_time - timesheet.get_clocking_time_in()).total_seconds()
            for timesheet in timesheets
        )

        # Convert total seconds to hours and minutes
        total_minutes, _ = divmod(total_hours, 60)
        total_hours, minutes = divmod(total_minutes, 60)

        return self.format_hours_minutes(total_hours, minutes)

    def get_employee_name(self):
        return f"{self.employee.first_name} {self.employee.last_name}" if self.employee else None
    get_employee_name.short_description = 'Employee'  # Custom column header


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

