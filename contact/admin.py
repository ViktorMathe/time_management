from django.contrib import admin
from .models import Contact, Reply

@admin.register(Contact)

@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    fields = (
        'email', 'subject', 'message',)