from django.urls import include, path
from . import views

urlpatterns = [
    path('contact/', views.contact, name='contact'),
    path('messages/', views.contact_messages, name='messages'),
    path('reply_messages/', views.reply_messages, name='reply_messages'),
    path('reply/<int:contact_id>', views.reply, name='reply')
]