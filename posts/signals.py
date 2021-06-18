from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Post
from .tasks import create_blur_placeholder


@receiver(post_save, sender=Post)
def run_placeholder_creation(sender, instance, created, **kwargs):
    if created:
        create_blur_placeholder.delay(instance.id)
