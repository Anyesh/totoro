from uuid import uuid4

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from totoro.utils import get_client_ip


# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        """
        Creates a totoro user with the given fields
        """

        user = self.model(
            username=username,
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username, email, password=password)

        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class Gender(models.Model):
    title = models.CharField(max_length=6, null=True, blank=True)

    def __str__(self):
        return self.title


class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(
        max_length=16, default=uuid4, primary_key=True, editable=False
    )
    username = models.CharField(max_length=16, unique=True, null=False, blank=False)
    email = models.EmailField(max_length=100, unique=True, null=False, blank=False)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    created_on = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    class Meta:
        verbose_name = "TotoroUser"


def upload_path(instance, filename):
    return "/".join(["avatars", str(instance.username), filename])


def cover_upload_path(instance, filename):
    return "/".join(["covers", str(instance.username), filename])


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE, null=True, blank=True)

    avatar = models.ImageField(blank=True, null=True, upload_to=upload_path)
    birthday = models.CharField(max_length=10, blank=True)
    tagline = models.CharField(max_length=200, blank=True, default="")
    hometown = models.CharField(max_length=100, blank=True, default="")
    work = models.CharField(max_length=100, blank=True, default="")
    cover_image = models.ImageField(blank=True, null=True, upload_to=cover_upload_path)
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )
    current_ip = models.CharField(max_length=20, blank=True, null=True)
    ip_list = models.JSONField(default=list, blank=True, null=True)

    # def save(self):
    #     if not self.id:
    #         self.password = generate_hash(self.password)
    #         super().save()

    def __str__(self):
        return "user: " + self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        ip = get_client_ip()
        Profile.objects.create(user=instance, current_ip=ip)
    instance.profile.save()
