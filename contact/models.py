from django.db import models
from manager.models import ManagerProfile
from employees.models import EmployeeProfile
from django.contrib.auth.models import User

class Contact(models.Model):
    sender = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, blank=True, null=True)
    recipient = models.ForeignKey(ManagerProfile, on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    subject = models.CharField(max_length=254)
    message = models.TextField()
    answered = models.BooleanField(default=False)

    def __str__(self):
        return f"From: {self.sender.user.username} To: {self.recipient.user.username}"


class Reply(models.Model):
    managers = models.ForeignKey(ManagerProfile, on_delete=models.CASCADE, blank=True, null=True)
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, blank=True, null=True)
    email = models.EmailField()
    subject = models.CharField(max_length=254)
    message = models.TextField()

    def __str__(self):
        return f'Re: {self.email}'