import os

from db_settings import initial


def db_initial():
    db_url = os.getcwd()
    if os.path.exists(db_url):
        print("exists DataBase, Next process")
        return True
    else:
        initial()
        print("create DataBase")


if __name__ == "__main__":
    db_initial()
