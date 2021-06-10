import re
import sys
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from PIL import Image

from accounts.models import User

RESIZE_THRESH = 0.08


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
            fix_spcl_char(str(instance.created_at)),
            rename(filename, suffix=f"{instance.height}x{instance.width}"),
        ]
    )


class ImageCollection(models.Model):
    width_field = models.IntegerField(default=0)
    height_field = models.IntegerField(default=0)
    url = models.ImageField(
        upload_to=upload_path,
        width_field="width_field",
        height_field="height_field",
        null=True,
        blank=True,
    )

    def __str__(self):
        return str(self.url)


class Posts(models.Model):
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

        self.thumbnail = self.compressImage(
            self.image, self.height * RESIZE_THRESH, self.width * RESIZE_THRESH
        )

        super(Posts, self).save(*args, **kwargs)

    def compressImage(self, uploaded_image, height, width):
        imageTemproary = Image.open(uploaded_image)
        imageTemproary = imageTemproary.convert("RGB")
        outputIoStream = BytesIO()
        imageTemproary.resize((int(width), int(height)))
        imageTemproary.save(outputIoStream, format="JPEG", quality=60)
        outputIoStream.seek(0)
        uploaded_image = InMemoryUploadedFile(
            outputIoStream,
            "ImageField",
            uploaded_image.name,
            "image/jpeg",
            sys.getsizeof(outputIoStream),
            None,
        )

        return uploaded_image


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
