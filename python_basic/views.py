import os, sqlite3
from crawling_pattern import school_daechi, school_dorim
import tasks


def view_control(number):
    db_path = os.getcwd() + '/data.db'
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    if number == 1:
        school_daechi.Crawling().detail_page()
        school_dorim.Crawling().detail_page()

    elif number == 2:
        print('All Table Join')
        # query = cur.execute("SELECT * FROM school_notice")
        query = cur.execute(
            '''
            SELECT *
            FROM school_notice
            '''
            # INNER
            # JOIN
            # notice_files
            # ON
            # school_notice.post_id = notice_files.post
        )

        print('-------------------------------------------------------------------------')
        for i in query.fetchall():
            print('Table -------------------------------------------------------------------')
            print('| id | post_id | school_name | subject | content | date | carwling_date |')
            print(f'| {i[0]} | {i[1]} | {i[2]} | {i[3]} | {i[4]} | {i[5]} | {i[6]} |', end="\n\n")
            file_query = cur.execute(
                f'''
                SELECT * FROM notice_files WHERE post = {i[1]}
                '''
            )

            print('Files --------------------------------------------------------')
            print('| id | post_id | file_subject | file_path | date | save_date |')
            for j in file_query.fetchall():
                print(f'| {j[0]} | {j[-1]} | {j[1]} | {j[2]} | {j[3]} | {j[4]} |', end="\n\n")
    elif number == 3:
        print('Celery Worker Add : Crawling process', end="\n\n")
        print('\n\n----------------------------------------\n\n')
        print('deachi elementary school Add', end="\n\n")
        tasks.run_crawling_daechi.delay()
        print('dorim elementary school Add')
        tasks.run_crawling_dorim.delay()
