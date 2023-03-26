# fastapi

피파온라인4 전적 검색 사이트

Python FastAPI Backend

## Run Setting
```
1. nexon PIPA api 가져오기.
- Nexon 공식 홈페이지 fifa api 신청 후 code 발급

2. Git Clone

3. Move Project Directory

4. 파이썬을 실행하기 위한 각종 라이브러리 설치

+++ python 버전 낮을 경우 아래의 명령어 실행
- $python.exe -m pip install --upgrade pip

- $pip install fastapi

-$pip install requests

-$pip install yarn

-$pip install pnpm

-$pip install pydantic

-$pip install uvicorn

+++ 만약 라이브러리 혹은 플러그인이 없어서 오류 발생시 해당 install 할것

5. main.py 실행
- 오류가 발생하지 않으면 6번으로 이동

6. 구동
- $uvicorn main:app --reload
