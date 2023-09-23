from django.db import models


class Contact(models.Model):
    phone_number = models.CharField(
        max_length=20, null=True, blank=True)
    email = models.EmailField()
    subject = models.CharField(max_length=254)
    message = models.TextField()
    answered = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.email


class Reply(models.Model):
    email = models.EmailField()
    subject = models.CharField(max_length=254)
    message = models.TextField()

    def __str__(self):
        return f'Re: {self.email}'