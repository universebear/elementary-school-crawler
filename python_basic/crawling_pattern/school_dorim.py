import os, sqlite3, requests, datetime, re
from bs4 import BeautifulSoup

__all__ = (
    'Crawling',
)


class Crawling:
    """
    도림 초등학교 패턴
    """
    school_data = {
        "school_name": "dorim",
        "board_id": [
            {
                "id": {"mcode": 1110, "cate": 1110},
                "category": "notice",
            },
            {
                "id": {"mcode": 1126, "cate": 1125},
                "category": "parents_notice"
            }
        ]
    }
    url = 'http://dorim.es.kr'
    db_path = os.getcwd() + '/data.db'

    def target_selection(self, board):
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        page_count = 1
        result_data = []
        parameter = {
            'mcode': board['id']['mcode'],
            'cate': board['id']['cate'],
            'page': page_count
        }
        response = requests.get(self.url + '/board.list?', parameter).text
        soup = BeautifulSoup(response, 'lxml')
        notice_list_data = soup.select('table.boardList > tbody > tr')
        third_day = datetime.date.today() - datetime.timedelta(days=5)

        while notice_list_data:
            source = notice_list_data.pop(0)
            post_date = source.select_one('tr > td:nth-of-type(5)').get_text().replace('.', '-')
            date_conversion = datetime.datetime.strptime(post_date, '%Y-%m-%d').date()
            post_id = int(re.findall('\d+', source.select_one('tr > td.title > a').get('href'))[1])
            post_subject = source.select_one('tr >  td.title > a').get_text()
            db_exists = cur.execute(
                f"""
                    SELECT EXiSTS (
                    SELECT school_name post_id FROM school_notice
                    WHERE (school_name = "{self.school_data['school_name']}") AND post_id = {post_id}
                    )
                """).fetchone()
            if '공지' in post_subject:
                continue
            elif date_conversion < third_day:
                # 처음 크롤링 시에 3일 전의 일자까지의 데이터만 출력한다.
                break
            elif db_exists[0]:
                # 해당하는 post id 가 db 에 존재할 경우 색인 작업을 중지한다.
                print(f"post id : {post_id} database exists")
                break
            elif not notice_list_data:
                # page 범위 내에 제약 일자가 없다면 다음 페이지로 이동 후 배열 업데이트
                page_count += 1
                parameter["page"] = page_count
                response = requests.get(self.url, parameter).text
                notice_list_data += BeautifulSoup(response, 'lxml').select('table.boardList > tbody > tr')
            result_data.append((post_id, post_date))
        return result_data

    def file_download(self):
        pass

    def detail_page(self):
        for board in self.school_data["board_id"]:
            print(f"\nCrawling start, {self.school_data['school_name']} : {board['category']}"
                  , end="\n\n")
            arr = self.target_selection(board)
            if not arr:
                # 데이터가 없을경우 원본의 업데이트가 없다고 판단
                print("Origin Website data is not update")
                continue

            result_data = []
            while arr:
                post_data = arr.pop(0)
                post_id = post_data[0]
                parameter = {
                    'mcode': board['id']['mcode'],
                    'id': post_id,
                }
                response = requests.get(self.url + '/board.read?', parameter).text
                soup = BeautifulSoup(response, 'lxml')
                post_subject = re.search(
                    '\s\w+.+', soup.select_one('div.boardReadHeader > div > dl > dd').get_text()
                ).group().strip()
                post_content = soup.select_one('div#contentBody').get_text(strip=True)
                result_data.append((post_id, self.school_data["school_name"], board["category"], post_subject,
                                    post_content, post_data[1]))
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            cur.executemany(
                "INSERT INTO school_notice (post_id, school_name, category, subject, contents, date) VALUES (?,?,?,?,?,?)",
                result_data
            )
            con.commit()
        print(f'Crawling End {self.school_data["school_name"]} elementary School')
        return True
