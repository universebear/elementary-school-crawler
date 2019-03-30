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
    school_name = '대치초등학교'
    header = {
        'Cookie': 'JSESSIONID=qGiWDLyKcx18QpKHZGXYsft7HrOn1pIBVWHIt61zhVe6TNLIUbMaTT1lYk81p8uf.hostingwas2_servlet_'
                  'engine7;Path=/;HttpOnly'
    }

    db_connect = initial()

    @property
    def target_selection(self):
        """
        크롤링 데이터 id 추출
        :return: list[(id, subject, date)...]
        """
        cur = self.db_connect["connect"].cursor()
        url = 'http://www.daechi.es.kr/dggb/module/board/selectBoardListAjax.do'
        page_count = 1
        parameter = {
            'bbsId': 'BBSMSTR_000000006692',
            'bbsTyCode': 'notice',
            'customRecordCountPerPage': 5,
            'pageIndex': page_count
        }
        print(self.db_connect["status"])
        response = requests.post(url, data=parameter, headers=self.header).text
        soup = BeautifulSoup(response, 'lxml')
        notice_list_data = soup.select('table > tbody > tr')
        third_day = datetime.date.today() - datetime.timedelta(days=3)
        result_data = []

        while notice_list_data:
            source = notice_list_data.pop(0)

            post_type = source.select_one("td:nth-of-type(1)").get_text()
            post_date = source.select_one("td:nth-of-type(4)").get_text()
            date_conversion = datetime.datetime.strptime(post_date, '%Y-%m-%d').date()
            post_id = int(re.findall('\d+', source.select_one("td.subject > a").get('onclick'))[1])
            post_subject = source.select_one("td.subject > a").get_text()
            db_exists = cur.execute(f"SELECT EXiSTS (SELECT 1 FROM school_notice WHERE post_id = {post_id})").fetchone()
            if '공지' in post_type:
                continue
            elif date_conversion < third_day and not self.db_connect["status"]:
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

    def file_download(self, html, date):
        soup = BeautifulSoup(html, 'lxml').select('tr > td > a')
        download_url = 'http://www.daechi.es.kr/dggb/board/boardFile/downFile.do'
        save_url = os.getcwd() + '/download_data/' + f'{date}/'

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
            print(f"file save : {file_subject}")

    def detail_page(self):
        """
        데이터 크롤링
        :return: boolean
        """
        url = 'http://www.daechi.es.kr/dggb/module/board/selectBoardDetailAjax.do'
        arr = self.target_selection
        if not arr:
            # 데이터가 없을경우 원본의 업데이트가 없다고 판단
            print("Origin Website data is not update")
            return False
        cur = self.db_connect["connect"].cursor()
        result_data = []
        while arr:
            post_data = arr.pop(0)
            post_id = post_data[0]
            parameter = {
                'bbsId': 'BBSMSTR_000000006692',
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
            result_data.append((post_id, self.school_name, 'notice', post_subject, post_content, post_date))
            file_list_html = ''.join(soup.find_all(string=lambda text: isinstance(text, Comment)))
            self.file_download(file_list_html, post_date)
        cur.executemany(
            "INSERT INTO school_notice (post_id, school_name, category, subject, contents, date) VALUES (?,?,?,?,?,?)",
            result_data
        )
        self.db_connect["connect"].commit()
        self.db_connect["connect"].close()
        print('Save end')
        return True
