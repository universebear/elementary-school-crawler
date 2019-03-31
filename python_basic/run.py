from crawling_pattern import school_daechi
from crawling_pattern import school_dorim
from db_settings import initial


def run_process():
    """
    process run
    :return:
    """

    # school_daechi.Crawling().detail_page()
    initial()
    school_daechi.Crawling().detail_page()
    school_dorim.Crawling().detail_page()


if __name__ == "__main__":
    run_process()
