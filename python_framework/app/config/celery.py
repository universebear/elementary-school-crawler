import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery('config', broker='redis://localhost:6379/0')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.update(
    CELERYBEAT_SCHEDULE={
        'run_crawler_dorim': {
            'task': 'boards.tasks.run_crawler_dorim',
            'schedule': crontab(hour='10,14,16,18', minute=0)
        },
        'run_crawler_daechi': {
            'task': 'boards.tasks.run_crawler_daechi',
            'schedule': crontab(hour='10,14,16,18', minute=0)
        }
    }
)