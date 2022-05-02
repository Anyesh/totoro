from django.db import models


# Create your models here.
class Friend(models.Model):

    user_a = models.CharField(max_length=16)
    user_b = models.CharField(max_length=16)
    since = models.FloatField()

    def __str__(self):
        return (
            "id: "
            + str(self.pk)
            + " => "
            + str(self.user_a)
            + " w/ "
            + str(self.user_b)
        )


class FriendRequest(models.Model):
    from_user = models.CharField(max_length=16)
    to_user = models.CharField(max_length=16)
    since = models.FloatField()

    def __str__(self):
        return f"from user: {str(self.from_user)} to user: {str(self.to_user)}"
