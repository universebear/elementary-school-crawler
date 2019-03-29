import sqlite3
import os

__all__ = (
    'initial',
)


def initial():
    work_dir = os.path.dirname(os.getcwd())
    con = sqlite3.connect(work_dir + '/data.db')
    cur = con.cursor()
    cur.execute(
        '''CREATE TABLE school_notice(
            id INTEGER NOT NULL PRIMARY KEY,
            post_id INTEGER NOT NULL,
            school_name TEXT NOT NULL,
            category TEXT NOT NULL,
            subject TEXT NOT NULL,
            contents TEXT,
            date DATE,
            crawling_date DATE DEFAULT CURRENT_DATE
        )'''
    )
    cur.execute(
        '''
        CREATE TABLE notice_files (
        id INTEGER NOT NULL PRIMARY KEY,
        file_name TEXT NOT NULL,
        file_url TEXT NOT NULL,
        crawling_date DATE DEFAULT CURRENT_DATE,
        post INTEGER NOT NULL,
        FOREIGN KEY (post) REFERENCES school_notice(id) ON DELETE CASCADE
    )'''
    )
    con.commit()
    con.close()
