from django.contrib.auth.models import User
from django.db import models


class Message(models.Model):
    sender = models.ForeignKey(User)
    subject = models.CharField(max_length=150)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', blank=True, null=True)

    def __str__(self):
        parent_status = "Yes" if self.parent else "No"
        return "From: {} , Subject {}, ParentStatus: {}".format(self.sender, self.subject, parent_status)

    @property
    def lastReply(self):
        return Message_Recipient.objects.filter(message__parent_id=self.id).order_by("-message__timestamp").first()

    @property
    def receiver(self):
        return Message_Recipient.objects.get(message=self).receiver

class Message_Recipient(models.Model):
    receiver = models.ForeignKey(User)
    message = models.ForeignKey("Message")

    def __str__(self):
        return "Message receiver {}, status: message:{}".format(self.receiver, self.message)


class Status(models.Model):
    user = models.ForeignKey(User)
    message = models.ForeignKey("Message", related_name="status_message")
    isRead = models.BooleanField(default=False)
    isDeleted = models.BooleanField(default=False)
