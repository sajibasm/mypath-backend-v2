import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rootApp.settings')  # ✅ correct project path

app = Celery('rootApp')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
