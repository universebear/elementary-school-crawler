import sqlite3, os

__all__ = (
    'initial',
)


def initial():
    """
    db 초기화
    """
    work_dir = os.getcwd()
    connect_data = {"connect": None, "status": False}
    if os.path.exists(work_dir + '/data.db'):
        connect_data["connect"] = sqlite3.connect(work_dir + '/data.db')
        connect_data["status"] = True
        return connect_data
    connect_data["connect"] = sqlite3.connect(work_dir + '/data.db')
    cur = connect_data["connect"].cursor()
    cur.execute(
        '''CREATE TABLE school_notice(
            id INTEGER NOT NULL PRIMARY KEY,
            post_id BLOB NOT NULL,
            school_name TEXT NOT NULL,
            category TEXT NOT NULL,
            subject TEXT NOT NULL,
            contents TEXT NOT NULL ,
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
    connect_data["connect"].commit()
    return connect_data
