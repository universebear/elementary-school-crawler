import datetime, re, requests, os, sqlite3
from bs4 import BeautifulSoup

__all__ = (
    'Crawling',
)


class Crawling:
    header = {
        'Cookie': 'WMONID=zwbOYIPbk-_; JSESSIONID=nKQR40n3rgLKMIewS21Uov0b74alg6JX4U2CkSWm1yXIABUUU1rSm5Ayd88TyLiT.hostingwas2_servlet_engine7'
    }

    @property
    def target_selection(self):
        """
        크롤링 데이터 id 추출
        :return: list[(id, subject, date)...]
        """
        url = 'http://www.daechi.es.kr/dggb/module/board/selectBoardListAjax.do'
        parameter = {
            'bbsId': 'BBSMSTR_000000006692',
            'bbsTyCode': 'notice',
            'customRecordCountPerPage': 20,
            'pageIndex': 1
        }

        response = requests.post(url, data=parameter, headers=self.header).text
        soup = BeautifulSoup(response, 'lxml')
        notic_list_data = soup.select('table > tbody > tr')
        third_day = datetime.date.today() - datetime.timedelta(days=3)
        result_data = []
        while notic_list_data:
            source = notic_list_data.pop(0)

            post_type = source.select_one("td:nth-of-type(1)").get_text()
            post_date = source.select_one("td:nth-of-type(4)").get_text()
            date_conversion = datetime.datetime.strptime(post_date, '%Y-%m-%d').date()

            if '공지' in post_type:
                continue
            elif date_conversion < third_day:
                break

            post_id = int(re.findall('\d+', source.select_one("td.subject > a").get('onclick'))[1])
            post_subject = source.select_one("td.subject > a").get_text()
            result_data.append((post_id, post_subject, post_date))
        return result_data

    def detail_page(self, con, cur):
        """
        초기 데이터 크롤링
        :param con: connection db
        :param cur: db cursor
        :return: boolean
        """
        url = 'http://www.daechi.es.kr/dggb/module/board/selectBoardDetailAjax.do'
        arr = self.target_selection
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
            result_data.append((post_id, '대치초등학교', 'notice', post_subject, post_content, post_date))

        cur.executemany(
            """
              INSERT INTO school_notice (post_id, school_name, category, subject, contents, date) VALUES (?,?,?,?,?,?)
            """, result_data
        )
        con.commit()
        print('Save end')
        return True
