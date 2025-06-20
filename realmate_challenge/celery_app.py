from celery import Celery
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "realmate_challenge.settings")

app = Celery("realmate_challenge")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
