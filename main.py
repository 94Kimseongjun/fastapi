import json

from fastapi import FastAPI, Request, Response, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests

# cmd : uvicorn main:app --reload
fifa4_api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJYLUFwcC1SYXRlLUxpbWl0IjoiNTAwOjEwIiwiYWNjb3VudF9pZCI6IjIwNjM5MjQyOTQiLCJhdXRoX2lkIjoiMiIsImV4cCI6MTY4OTA1Mjg5MiwiaWF0IjoxNjczNTAwODkyLCJuYmYiOjE2NzM1MDA4OTIsInNlcnZpY2VfaWQiOiI0MzAwMTE0ODEiLCJ0b2tlbl90eXBlIjoiQWNjZXNzVG9rZW4ifQ.Zltg5nSZfLzyZ6dBlGZD9fmoLoIMt0xXkP7yZv-AgUY"
header = {
    'Authorization': fifa4_api_key
}

division_dict={
    800:"슈퍼챔피언스",
    900: "챔피언스",
    1000: "슈퍼챌린지",
    1100: "챌린지1",
    1200: "챌린지2",
    1300: "챌린지3",
    2000: "월드클래스1",
    2100: "월드클래스2",
    2200: "월드클래스3",
    2300: "프로1",
    2400: "프로2",
    2500: "프로3",
    2600: "세미프로1",
    2700: "세미프로2",
    2800: "세미프로3",
    2900: "유망주1",
    3000: "유망주2",
    3100: "유망주3"
}




app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class SearchUserData(BaseModel):
    nickName: str

@app.post("/searchNickName")
async def search_nick_name(data: SearchUserData):
    fifa4_nick_name_api_url="https://api.nexon.co.kr/fifaonline4/v1.0/users?nickname={}"
    fifa4_maxdivision_api_url="https://api.nexon.co.kr/fifaonline4/v1.0/users/{}/maxdivision"
    result={"accessId": "", "nickname":"","level":"","rank":"","autoRank":""}
    try:
        nick_name_response = requests.get(fifa4_nick_name_api_url.format(data.nickName), headers=header)
        if nick_name_response.status_code == 200:
            """
            accessId	String	유저 고유 식별자 
            nickname	String	유저 닉네임 
            level	Integer	유저 레벨 
            """
            nick_name_jsonStr = nick_name_response.json()
            accessId = nick_name_jsonStr['accessId']
            nickname = nick_name_jsonStr['nickname']
            level = nick_name_jsonStr['level']
            result["accessId"] = accessId
            result["nickname"] = nickname
            result["level"] = level

            maxdivision_response = requests.get(fifa4_maxdivision_api_url.format(accessId), headers=header)
            if maxdivision_response.status_code == 200:
                maxdivision_jsonStr = maxdivision_response.json()
                for maxdivision_info in maxdivision_jsonStr:
                    matchType = maxdivision_info['matchType']
                    division = maxdivision_info['division']
                    achievementDate = maxdivision_info['achievementDate']
                    maxdivision_info['division'] = division_dict[division]
                    temp_time = achievementDate.split("T")
                    maxdivision_info['achievementDate'] = temp_time[0]
                    if matchType==50: # 공식경기
                        maxdivision_info['matchType'] = '공식경기'
                        result["rank"] = maxdivision_info
                    elif matchType==52: # 감독모드
                        maxdivision_info['matchType'] = '감독모드'
                        result["autoRank"] = maxdivision_info
                print(result)
                #result = json.dumps(result,ensure_ascii = False)
                return result
            else:
                raise HTTPException(status_code=maxdivision_response.status_code, detail=maxdivision_response.text)
        else:
            raise HTTPException(status_code=nick_name_response.status_code, detail=nick_name_response.text)
    except requests.RequestException as error:
        raise HTTPException(status_code=500, detail=str(error))

