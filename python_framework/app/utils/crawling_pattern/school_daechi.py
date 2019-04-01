import datetime, re, requests
from bs4 import BeautifulSoup, Comment
from django.core.files.base import ContentFile

from boards import models


class Crawling:
    """
    서울 대치 초등학교 패턴
    """

    school_data = {
        "school_name": "daechi",
        "board_id": [
            {
                "id": "BBSMSTR_000000006692",
                "category": "n",
            },
            {
                "id": "BBSMSTR_000000006693",
                "category": "p"
            }
        ]
    }

    # cookie 에 token 이 없으면 실행이 안됨으로 한번 메인페이지를 방문하여 token 발급 후 진행
    header = {
        'Cookie': ''.join(
            sorted(
                [f'{i.name}={i.value};' for i in requests.get('http://daechi.es.kr/20465/subMenu.do').cookies],
                reverse=True
            )
        )
    }

    def target_selection(self, board):
        """
        크롤링할 post 의 id 선별
        :param board:
        :return: list[(id, subject, date)...]
        """
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
        third_day = datetime.date.today() - datetime.timedelta(days=5)
        while notice_list_data:
            source = notice_list_data.pop(0)
            post_type = source.select_one("td:nth-of-type(1)").get_text()
            post_date = source.select_one("td:nth-of-type(4)").get_text()
            date_conversion = datetime.datetime.strptime(post_date, '%Y-%m-%d').date()
            post_id = int(re.findall('\d+', source.select_one("td.subject > a").get('onclick'))[1])
            post_subject = source.select_one("td.subject > a").get_text()

            if '공지' in post_type:
                continue
            elif date_conversion < third_day:
                # page 범위 내에 제약 일자가 없다면 다음 페이지로 이동 후 배열 업데이트
                break
            elif models.Board.objects.filter(post_id=post_id, school_name=self.school_data['school_name'],
                                             category=board['category']).exists():
                # 해당하는 post id 가 db 에 존재할 경우 색인 작업을 중지한다.
                break
            elif not notice_list_data:
                # page 범위 내에 제약 일자가 없다면 다음 페이지로 이동 후 배열 업데이트
                page_count += 1
                parameter["pageIndex"] = page_count
                response = requests.post(url, data=parameter, headers=self.header).text
                notice_list_data += BeautifulSoup(response, 'lxml').select('table > tbody > tr')
            result_data.append((post_id, post_subject, date_conversion))

        return result_data

    def file_download(self, html, post_id, date, category):
        """
        순차적 파일 다운로드
        쿼리를 여러번 조회, 개선방법 찾아보기
        :param html: file 정보를 포함한 html comment text, javascript 데이터 동적 로드로 차선책
        :param post_id: 관계를 연결할 post_id
        :param date: 생성일자
        """
        soup = BeautifulSoup(html, 'lxml').select('tr > td > a')
        download_url = 'http://www.daechi.es.kr/dggb/board/boardFile/downFile.do'
        while soup:
            file_data = soup.pop(0)
            file_id = re.search(r'FILE\D\d+', file_data.get('href')).group()
            file_number = int(re.search(r"\D[0-9]\D", file_data.get('href')).group().replace("'", ""))
            file_subject = re.search(r'\w*.+\.\w+', file_data.get_text(strip=True)).group()

            parameter = {
                "atchFileId": file_id,
                "fileSn": file_number
            }
            post = models.Board.objects.get(post_id=post_id, school_name=self.school_data['school_name'],
                                            category=category)
            response = requests.get(download_url, parameter, headers=self.header, stream=True)

            file_data, file_model = models.FileBoard.objects.update_or_create(post=post, subject=file_subject)
            file_data.file.save(f'{date}/' + file_subject, ContentFile(response.content))

            # result_data.append(file_model)
        # models.FileBoard.objects.bulk_create(result_data)

    def school_crawler(self):
        """
        크롤링 메서드
        :return:
        """
        url = 'http://www.daechi.es.kr/dggb/module/board/selectBoardDetailAjax.do'
        for board in self.school_data["board_id"]:
            arr = self.target_selection(board)
            if not arr:
                # 데이터가 없을경우 원본의 업데이트가 없다고 판단
                print("Origin Website data is not update")
                continue
            result_data = []
            file_download_list = []
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
                result_data.append(
                    models.Board(post_id=post_id, subject=post_subject, content=post_content,
                                 school_name=self.school_data["school_name"], category=board["category"],
                                 post_date=post_date
                                 ))

                file_list_html = ''.join(soup.find_all(string=lambda text: isinstance(text, Comment)))
                file_download_list.append((file_list_html, post_id, post_date, board['category']))
            models.Board.objects.bulk_create(result_data)
            while file_download_list:
                data = file_download_list.pop(0)
                self.file_download(data[0], data[1], data[2], data[3])
