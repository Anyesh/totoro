from django.db import models

# Create your models here.
class Notification(models.Model):
    # seen: 0 (not-seen) or 1 (seen)
    seen = models.IntegerField(default=0)

    # noti: notification type _> 0: post like, 1: new comment, 2: comment like, 3: new friend req, 4: friend request accepted
    # 5: comment reply
    noti = models.IntegerField()

    user_for = models.IntegerField()
    user_from = models.IntegerField()

    # about: _> friend or post
    about = models.IntegerField()

    created = models.FloatField()

    def __str__(self):
        return (
            "Notification #"
            + str(self.pk)
            + " __for "
            + str(self.user_for)
            + " __from "
            + str(self.user_from)
        )
