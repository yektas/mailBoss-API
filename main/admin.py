from django.contrib import admin

from main.models import Message, Message_Recipient

admin.site.register(Message)
admin.site.register(Message_Recipient)
