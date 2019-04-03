# Elementary School Crawler

면접 과제로 제작된 초등학교 홈페이지 크롤러입니다.

테스트 환경 mac os mojave 10.14.4 / python 3.7.1

## Setting & Installs

pyenv & pip install 의 경우

```bash
~/elementary-school-crawler/
>> pip install -r requirements.txt
```

pipenv install 의 경우

```bash
~/elementary-school-crawler/
>> pipenv install
```

두 경우 다 가상환경에 접속한다. `pipenv` 의 경우 pipenv shell 로 접속

## Crawling Schools

- [도림 초등학교](http://dorim.es.kr/main)
- [대치 초등학교](http://www.daechi.es.kr/index.do)

## Crawling Data & 기능

- 공지사항
- 가정통신문
- 각 포스트 내부의 첨부파일
- DB 에 저장
- 처음 크롤링시에 오늘부터 3일 전 데이터만 가져오기(도림 초등학교의 경우 테스트 당시 3일 전 데이터가 없어 5일전으로 설정했습니다.)
- DB 에 있는 데이터는 무시
- 스케쥴러 기능으로 일 3회 자동으로 크롤링

## Version

파이썬과 그 라이브러리로 제작한 크롤러와 프레임워크 `django` 를 사용하여 제작한 크롤러 하나를 준비했습니다.

- [python_basic](https://github.com/Younlab/elementary-school-crawler/tree/master/python_basic)
- [python_framework](https://github.com/Younlab/elementary-school-crawler/tree/master/python_framework)

## DB

로컬 세팅이 용의하게 `sqlite3` 를 사용했습니다.
