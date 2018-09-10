from django.contrib.auth.models import User
from django.db import models


class Email(models.Model):
    from_user = models.ForeignKey(User, related_name="from_user")
    to_user = models.ForeignKey(User, related_name="to_user")
    subject = models.CharField(max_length=150)
    content = models.TextField()
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Mail from {} to {}".format(self.from_user.username, self.to_user.username)