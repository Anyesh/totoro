import base64
from io import BytesIO

import blurhash
import numpy as np
from celery import shared_task
from django.db import IntegrityError, transaction
from PIL import Image

from .models import Post


@shared_task(
    bind=True,
    autoretry_for=(IntegrityError,),
    retry_kwargs={"max_retries": 3, "countdown": 15},
)
def create_blur_placeholder(self, pk):
    try:
        post = Post.objects.filter(pk=pk)
        im = np.asarray(Image.open(post.first().image).convert("RGB"))
        hash = blurhash.encode(im, components_x=4, components_y=3)
        img = Image.fromarray(np.asarray(blurhash.decode(hash, 32, 32)).astype("uint8"))
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        final_bs = (
            "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()
        )
        with transaction.atomic():
            post.update(placeholder=final_bs)
            # post.save()
    except IntegrityError:
        raise IntegrityError(
            "One of the trasnsaction didn't work properly so all transactions rolled back"
        )
