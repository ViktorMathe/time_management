from django.contrib import admin
from .models import Contact_us, Reply


@admin.register(Contact_us)
class ContactUsAdmin(admin.ModelAdmin):
    readonly_fields = (
        'phone_number', 'email', 'subject', 'message',)


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    fields = (
        'email', 'subject', 'message',)