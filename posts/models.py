import base64
import re
import uuid
from datetime import datetime
from io import BytesIO

import blurhash
import numpy as np
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image

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


class ResizeImageMixin:
    def create_placeholder(self, image):
        im = np.asarray(Image.open(image).convert("RGB"))
        hash = blurhash.encode(im, components_x=4, components_y=3)
        img = Image.fromarray(np.asarray(blurhash.decode(hash, 12, 12)).astype("uint8"))
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()

    def resize(self, imageField, thumbnail, size: tuple):
        im = Image.open(imageField)  # Catch original
        source_image = im.convert("RGB")
        source_image.thumbnail(size)  # Resize to size
        output = BytesIO()
        source_image.save(output, format="JPEG")  # Save resize image to bytes
        output.seek(0)

        content_file = ContentFile(
            output.read()
        )  # Read output and create ContentFile in memory
        file = File(content_file)

        random_name = f"{uuid.uuid4()}.jpeg"
        thumbnail.save(random_name, file, save=False)


class Post(models.Model, ResizeImageMixin):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.TextField()
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
        return "Post " + str(self.pk) + ", by " + str(self.author.username)

    def save(self, *args, **kwargs):
        if not self.pk:

            self.resize(
                self.image,
                self.thumbnail,
                (int(self.height * RESIZE_THRESH), int(self.width * RESIZE_THRESH)),
            )

            self.is_published = True

        super(Post, self).save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_text = models.TextField(blank=False)
    comment_likes = models.JSONField(default=dict)
    comment_parent = models.CharField(max_length=16)
    created = models.FloatField()
    updated = models.FloatField()

    def __str__(self):
        return "Comment #" + str(self.pk) + " __by " + str(self.user.user_id)
