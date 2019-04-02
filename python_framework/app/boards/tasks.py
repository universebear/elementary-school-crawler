from config.celery import app
from .patterns import school_dorim, school_daechi


@app.task
def run_crawler_dorim():
    print('run dorim crawler')
    school_daechi.Crawling().school_crawler()


@app.task
def run_crawler_daechi():
    print('run daechi crawler')
    school_dorim.Crawling().school_crawler()
