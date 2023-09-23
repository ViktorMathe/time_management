from django.contrib import admin
from .models import Contact, Reply


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    readonly_fields = (
        'phone_number', 'email', 'subject', 'message',)


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    fields = (
        'email', 'subject', 'message',)