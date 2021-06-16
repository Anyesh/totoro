import os

from celery import Celery

# from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "totoro.settings")

app = Celery("totoro")
app.config_from_object("django.conf:settings")
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
