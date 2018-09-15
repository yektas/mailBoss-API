from django.contrib.auth.models import User
from django.db import models


class Message(models.Model):
    sender = models.ForeignKey(User)
    subject = models.CharField(max_length=150)
    body = models.TextField()
    isRead = models.BooleanField(default=True)
    isDeleted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', blank=True, null=True)

    def __str__(self):
        parent_status = "Yes" if self.parent else "No"
        return "From: {} , Subject {}, ParentStatus: {}".format(self.sender, self.subject, parent_status)

    @property
    def receiver(self):
        return Message_Recipient.objects.get(message__id=self.id).receiver


class Message_Recipient(models.Model):
    receiver = models.ForeignKey(User)
    message = models.ForeignKey("Message")
    isRead = models.BooleanField(default=False)
    isDeleted = models.BooleanField(default=False)

    def __str__(self):
        return "Message receiver {}, status: isRead:{} isDeleted:{} message:{}".format(self.receiver, self.isRead,
                                                                                       self.isDeleted, self.message)
