import os, sqlite3

from db_settings import initial
from crawling_pattern import school_daechi


def db_initial():
    """
    db initial
    :return:
    """
    # db_url = os.getcwd() + '/data.db'

    school_daechi.Crawling().detail_page()


if __name__ == "__main__":
    db_initial()
