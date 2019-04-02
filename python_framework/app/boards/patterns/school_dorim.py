import requests
import datetime
import re
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile

from ..models import Board, FileBoard


class Crawling:
    """
    도림 초등학교 패턴
    """
    school_data = {
        "school_name": "dorim",
        "board_id": [
            {
                "id": {"mcode": 1110, "cate": 1110},
                "category": "n",
            },
            {
                "id": {"mcode": 1126, "cate": 1125},
                "category": "p"
            }
        ]
    }
    url = 'http://dorim.es.kr'

    def target_selection(self, board):
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
        third_day = datetime.date.today() - datetime.timedelta(days=6)

        while notice_list_data:
            source = notice_list_data.pop(0)
            post_date = source.select_one('tr > td:nth-of-type(5)').get_text().replace('.', '-')
            date_conversion = datetime.datetime.strptime(post_date, '%Y-%m-%d').date()
            post_id = int(re.findall('\d+', source.select_one('tr > td.title > a').get('href'))[1])
            post_subject = source.select_one('tr >  td.title > a').get_text()

            if '공지' in post_subject:
                continue
            elif date_conversion < third_day:
                # 처음 크롤링 시에 3일 전의 일자까지의 데이터만 출력한다.
                break
            elif Board.objects.filter(post_id=post_id, school_name=self.school_data['school_name'],
                                      category=board['category']).exists():
                # 해당하는 post id 가 db 에 존재할 경우 색인 작업을 중지한다.
                break
            elif not notice_list_data:
                # page 범위 내에 제약 일자가 없다면 다음 페이지로 이동 후 배열 업데이트
                page_count += 1
                parameter["page"] = page_count
                response = requests.get(self.url, parameter).text
                notice_list_data += BeautifulSoup(response, 'lxml').select('table.boardList > tbody > tr')
            result_data.append((post_id, date_conversion))
        return result_data

    def file_download(self, html, post_id, date, category):
        """
        순차적 파일 다운로드
        쿼리를 여러번 조회, 개선방법 찾아보기
        :param html: file 정보를 포함한 html comment text, javascript 데이터 동적 로드로 차선책
        :param post_id: 관계를 연결할 post_id
        :param date: 생성일자
        """
        while html:
            file_data = html.pop(0)
            download_url = file_data.select_one('tr > td > a').get('href')
            file_subject = file_data.select_one('tr > td > a').get_text()
            post = Board.objects.get(post_id=post_id, school_name=self.school_data['school_name'],
                                     category=category)
            response = requests.get(download_url)

            file_data, file_model = FileBoard.objects.update_or_create(post=post, subject=file_subject)
            file_data.file.save(f'{date}/' + file_subject, ContentFile(response.content))

    def school_crawler(self):
        """
        크롤링 메서드
        :return:
        """
        for board in self.school_data["board_id"]:
            print(f"\nCrawling start, {self.school_data['school_name']} : {board['category']}"
                  , end="\n\n")
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
                    'mcode': board['id']['mcode'],
                    'id': post_id,
                }
                response = requests.get(self.url + '/board.read?', parameter).text
                soup = BeautifulSoup(response, 'lxml')
                post_subject = re.search(
                    '\s\w+.+', soup.select_one('div.boardReadHeader > div > dl > dd').get_text()
                ).group().strip()
                post_content = soup.select_one('div#contentBody').get_text(strip=True)
                result_data.append(
                    Board(post_id=post_id, subject=post_subject, content=post_content,
                          school_name=self.school_data["school_name"], category=board["category"],
                          post_date=post_data[1]
                          ))

                post_file_list = soup.select('div.boradReadFooter > table > tr > td:nth-of-type(2) > table > tr')
                file_download_list.append((post_file_list, post_id, post_data[1], board['category']))
            Board.objects.bulk_create(result_data)
            while file_download_list:
                data = file_download_list.pop(0)
                self.file_download(data[0], data[1], data[2], data[3])

        print(f'Crawling End {self.school_data["school_name"]} elementary School')
