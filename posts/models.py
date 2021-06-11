import re
import uuid
from datetime import datetime
from io import BytesIO

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


class Posts(models.Model, ResizeImageMixin):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.TextField()
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    image = models.ImageField(
        width_field="width",
        height_field="height",
        upload_to=upload_path,
    )
    thumbnail = models.ImageField(blank=True, null=True, upload_to=upload_path)
    likes = models.JSONField(default=dict, blank=True, null=True)
    categories = models.JSONField(default=list, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Post " + str(self.pk) + ", by " + str(self.author.username)

    def save(self, *args, **kwargs):

        self.resize(
            self.image,
            self.thumbnail,
            (int(self.height * RESIZE_THRESH), int(self.width * RESIZE_THRESH)),
        )

        super(Posts, self).save(*args, **kwargs)


class Comment(models.Model):
    # comment_parent if equal to pk then comment is top level comment
    post_id = models.CharField(max_length=16)
    user_id = models.CharField(max_length=16)
    comment_text = models.TextField(blank=False)
    comment_likes = models.JSONField(default=dict)
    comment_parent = models.CharField(max_length=16)
    created = models.FloatField()
    updated = models.FloatField()

    def __str__(self):
        return "Comment #" + str(self.pk) + " __by " + str(self.user_id)
