from celery import Celery
from celery.schedules import crontab
from crawling_pattern import school_daechi
from db_settings import initial

app = Celery(
    'tasks',
    broker='redis://localhost:6378/0',
)
app.conf.update(
    enable_utc=False,
    timezone='Asia/Seoul'
)
# app.conf.beat_schedule = {
#     'add-crawling-logic': {
#         'task': 'tasks.run_crawling',
#         'schedule': 10.0,
#         # 'args': (1, 2)
#     }
# }


# crontab(hour='9,14,18', minute=0)

@app.task
def run_crawling():
    school_daechi.Crawling().detail_page()


@app.task
def add(x, y):
    return x + y
