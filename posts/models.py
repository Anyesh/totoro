import re
from datetime import datetime

from django.db import models

from accounts.models import User

RESIZE_THRESH = 0.6


def rename(filename, suffix=None):
    if not suffix:
        return filename

    ext = filename.split(".")[-1]
    fn = filename[: -(len(ext) + 1)]
    return fn + "-" + suffix + "." + ext


def fix_spcl_char(chars):
    return re.sub(r"[(\s\.\-\:)]", "-", chars)


def upload_path(instance, filename):
    return "/".join(
        [
            "posts",
            str(instance.author.username),
            fix_spcl_char(str(datetime.now())),
            rename(filename, suffix=f"{instance.height}x{instance.width}"),
        ]
    )


class Post(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.SET(User.objects.get(username="deleted_user").user_id),
        null=True,
    )
    origin = models.JSONField(null=True, blank=True, default=dict)
    title = models.CharField(max_length=120)
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    image = models.ImageField(
        width_field="width",
        height_field="height",
        upload_to=upload_path,
    )
    thumbnail = models.ImageField(blank=True, null=False, upload_to=upload_path)
    placeholder = models.TextField(
        null=True,
        blank=True,
        default="data:image/jpeg;base64,/9j/\
            2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/\
            2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/\
            wAARCAAIAAoDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAb/xAAhEAACAQMDBQAAAAAAAAAAAAABAgMABAUGIWEREiMxUf/\
            EABUBAQEAAAAAAAAAAAAAAAAAAAMF/8QAGhEAAgIDAAAAAAAAAAAAAAAAAAECEgMRkf/aAAwDAQACEQMRAD8AltJagyeH0AthI5x\
            drLcNM91BF5pX2HaH9bcfaSXWGaRmknyJckliyjqTzSlT54b6bk+h0R//2Q==",
    )
    likes = models.JSONField(default=dict, blank=True, null=True)
    is_published = models.BooleanField(default=False, blank=True, null=True)
    categories = models.JSONField(default=list, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Post " + str(self.pk) + " __by " + str(self.author.username)

    def save(self, *args, **kwargs):
        # if self.image:
        self.thumbnail = self.image
        super(Post, self).save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User,
        on_delete=models.SET(User.objects.get(username="deleted_user").user_id),
        null=True,
    )
    comment_text = models.TextField(blank=False)
    comment_likes = models.JSONField(default=dict, blank=True, null=True)
    comment_parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Comment #" + str(self.pk) + " __by " + str(self.user.username)
