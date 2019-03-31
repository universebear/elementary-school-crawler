from celery import Celery
from celery.schedules import crontab
from crawling_pattern import school_daechi, school_dorim
from db_settings import initial

app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
)
app.conf.update(
    enable_utc=False,
    timezone='Asia/Seoul'
)
app.conf.beat_schedule = {
    'add-crawling-logic': {
        'task': 'tasks.run_crawling',
        'schedule': crontab(hour='9,14,18', minute=0)
    }
}


@app.task
def run_crawling():
    initial()
    school_daechi.Crawling().detail_page()
    school_dorim.Crawling().detail_page()


