from django.db import models

# Create your models here.
class Business(models.Model):
    """ Business model """
    business_name = models.CharField(max_length=1024)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.business_name


class ManagerProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.IntegerField(blank=True, null=True)
    company = models.ForeignKey(Business, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name