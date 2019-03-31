import datetime, re, requests, os, sqlite3
from bs4 import BeautifulSoup, Comment
from db_settings import initial

__all__ = (
    'Crawling',
)


class Crawling:
    """
    서울 대치초등학교 패턴
    """
    school_data = {
        "school_name": "daechi",
        "board_id": [
            {
                "id": "BBSMSTR_000000006692",
                "category": "notice",
            },
            {
                "id": "BBSMSTR_000000006693",
                "category": "parents_notice"
            }
        ]
    }
    header = {
        'Cookie': ''.join(
            sorted(
                [f'{i.name}={i.value};' for i in requests.get('http://daechi.es.kr/20465/subMenu.do').cookies],
                reverse=True
            )
        )
    }

    # db_connect = initial()
    db_path = os.getcwd() + '/data.db'

    def target_selection(self, board):
        """
        크롤링 데이터 id 추출
        :return: list[(id, subject, date)...]
        """
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        url = 'http://www.daechi.es.kr/dggb/module/board/selectBoardListAjax.do'
        page_count = 1
        result_data = []

        parameter = {
            'bbsId': board["id"],
            'bbsTyCode': 'notice',
            'customRecordCountPerPage': 5,
            'pageIndex': page_count
        }
        response = requests.post(url, data=parameter, headers=self.header).text
        soup = BeautifulSoup(response, 'lxml')
        notice_list_data = soup.select('table > tbody > tr')
        third_day = datetime.date.today() - datetime.timedelta(days=3)

        while notice_list_data:
            source = notice_list_data.pop(0)
            post_type = source.select_one("td:nth-of-type(1)").get_text()
            post_date = source.select_one("td:nth-of-type(4)").get_text()
            date_conversion = datetime.datetime.strptime(post_date, '%Y-%m-%d').date()
            post_id = int(re.findall('\d+', source.select_one("td.subject > a").get('onclick'))[1])
            post_subject = source.select_one("td.subject > a").get_text()
            db_exists = cur.execute(
                f"""
                    SELECT EXiSTS (
                    SELECT school_name post_id FROM school_notice
                    WHERE (school_name = "{self.school_data['school_name']}") AND post_id = {post_id}
                    )
                """).fetchone()

            if '공지' in post_type:
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
                parameter["pageIndex"] = page_count
                response = requests.post(url, data=parameter, headers=self.header).text
                notice_list_data += BeautifulSoup(response, 'lxml').select('table > tbody > tr')

            result_data.append((post_id, post_subject, post_date))
        return result_data

    def file_download(self, html, post_id, date):
        """
        순차적 파일 다운로드
        :param html: file 정보를 포함한 html comment text, javascript 데이터 동적 로드로 차선책
        :param post_id: 관계를 연결할 post_id
        :param date: 생성일자
        :return: boolean
        """
        soup = BeautifulSoup(html, 'lxml').select('tr > td > a')
        download_url = 'http://www.daechi.es.kr/dggb/board/boardFile/downFile.do'
        save_url = os.getcwd() + '/download_data/' + f'{date}/'
        result_data = []
        if not os.path.exists(save_url):
            os.mkdir(save_url)

        while soup:
            file_data = soup.pop(0)
            file_id = re.search(r'FILE\D\d+', file_data.get('href')).group()
            file_number = int(re.search(r"\D[0-9]\D", file_data.get('href')).group().replace("'", ""))
            file_subject = re.search(r'\w*.+\.\w+', file_data.get_text(strip=True)).group()
            file_url = save_url + file_subject

            parameter = {
                "atchFileId": file_id,
                "fileSn": file_number
            }
            response = requests.get(download_url, parameter, headers=self.header, stream=True)
            with response as r:
                r.raise_for_status()
                with open(file_url, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            result_data.append((post_id, file_subject, file_url, date))
            print(f"file save : {file_subject}")

        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        cur.executemany(
            """INSERT INTO notice_files (post, file_subject, file_url, date) VALUES (?,?,?,?)""",
            result_data
        )
        con.commit()
        print("files path database save")
        return True

    def detail_page(self):
        """
        데이터 크롤링
        :return: boolean
        """
        # initial()
        url = 'http://www.daechi.es.kr/dggb/module/board/selectBoardDetailAjax.do'
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
                    'bbsId': board["id"],
                    'bbsTyCode': 'notice',
                    'customRecordCountPerPage': 1,
                    'pageIndex': 1,
                    'nttId': post_id
                }
                response = requests.post(url, headers=self.header, data=parameter).text
                soup = BeautifulSoup(response, 'lxml')
                post_subject = post_data[1]
                post_date = post_data[2]
                post_content = soup.select_one('div.content').get_text(strip=True)
                result_data.append((post_id, self.school_data["school_name"], board["category"], post_subject,
                                    post_content, post_date))
                file_list_html = ''.join(soup.find_all(string=lambda text: isinstance(text, Comment)))
                self.file_download(file_list_html, post_id, post_date)
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            cur.executemany(
                "INSERT INTO school_notice (post_id, school_name, category, subject, contents, date) VALUES (?,?,?,?,?,?)",
                result_data
            )
            con.commit()
        print(f'Crawling End {self.school_data["school_name"]} elementary School')
        return True
