from views import view_control
from db_settings import initial


def run_process():
    """
    process run
    :return:
    """
    initial()
    while True:
        print(
            '''
            원하는 기능의 번호를 입력하세요\n
            1. 크롤링 시작\n
            2. DB 의 모든 내용 조회\n
            0. Exit
            '''
        )
        key = int(input())
        if key == 0:
            break
        view_control(key)


if __name__ == "__main__":
    run_process()
