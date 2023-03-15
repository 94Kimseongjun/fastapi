import json

from fastapi import FastAPI, Request, Response, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests

# cmd : uvicorn main:app --reload

with open('api_key.json','r') as f:
    json_data = json.load(f)
fifa4_api_key = json_data['fifa4_api_key']

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

"""
class SearchUserData(BaseModel):
    nickName: str
"""

def call_nexon_api(url):
    try:
        response = requests.get(url, headers=header)
        if response.status_code==200:
            return response
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except requests.RequestException as error:
        raise HTTPException(status_code=500, detail=str(error))



@app.get("/searchNickName")
async def search_nick_name(nickName: str):
    # 최종 결과값
    result = {
        "accessId": "",
        "nickname": "",
        "level": "",
        "rank": "",
        "autoRank": "",
        "matchList": ""
    }

    # nickName 으로 accessId,level 가져오기
    fifa4_nick_name_api_url="https://api.nexon.co.kr/fifaonline4/v1.0/users?nickname={}".format(nickName)
    nick_name_response = call_nexon_api(fifa4_nick_name_api_url)

    if nick_name_response:
        nick_name_jsonStr = nick_name_response.json()
        accessId = nick_name_jsonStr['accessId']
        nickname = nick_name_jsonStr['nickname']
        level = nick_name_jsonStr['level']
        result["accessId"] = accessId
        result["nickname"] = nickname
        result["level"] = level
    else:
        raise HTTPException(status_code=nick_name_response.status_code, detail=nick_name_response.text)

    # accessId로 최고등급 가져오기
    fifa4_maxdivision_api_url="https://api.nexon.co.kr/fifaonline4/v1.0/users/{}/maxdivision".format(accessId)
    maxdivision_response = call_nexon_api(fifa4_maxdivision_api_url)
    if maxdivision_response:
        maxdivision_jsonStr = maxdivision_response.json()
        for maxdivision_info in maxdivision_jsonStr:
            matchType = maxdivision_info['matchType']
            division = maxdivision_info['division']
            achievementDate = maxdivision_info['achievementDate']
            maxdivision_info['division'] = division_dict[division]
            temp_time = achievementDate.split("T")
            maxdivision_info['achievementDate'] = temp_time[0]
            if matchType == 50:  # 공식경기
                maxdivision_info['matchType'] = '공식경기'
                result["rank"] = maxdivision_info
            elif matchType == 52:  # 감독모드
                maxdivision_info['matchType'] = '감독모드'
                result["autoRank"] = maxdivision_info
    else:
        raise HTTPException(status_code=maxdivision_response.status_code, detail=maxdivision_response.text)


    match_history_api_url = "https://api.nexon.co.kr/fifaonline4/v1.0/users/{accessid}/matches?matchtype={matchtype}&offset={offset}&limit={limit}".format(accessid=accessId,matchtype=50,offset=0,limit=20)
    match_history_response = call_nexon_api(match_history_api_url)
    match_list = []
    if match_history_response:
        match_id_list = match_history_response.json()
        # 최근 20경기 분석 후 평균 점유율, 헤더 시도 비율, 중거리 슛 시도 비율 가져오기
        detail_match_api_url = "https://api.nexon.co.kr/fifaonline4/v1.0/matches/{matchid}"
        cnt = 0
        for match_id in match_id_list:

            detail_match_response = call_nexon_api(detail_match_api_url.format(matchid=match_id))
            if detail_match_response:
                detail_match = detail_match_response.json()
                match_list.append(detail_match)
                #matchId = detail_match["matchId"]
                #matchDate = detail_match["matchDate"]
                #matchInfo = detail_match["matchInfo"]
            cnt += 1
            if cnt == 10:
                break
        result["matchList"] = match_list
    else:
        raise HTTPException(status_code=match_history_response.status_code, detail=match_history_response.text)
    return result


"""  
@app.get("/searchNickName")
async def search_nick_name(nickName: str):
    fifa4_nick_name_api_url="https://api.nexon.co.kr/fifaonline4/v1.0/users?nickname={}"
    fifa4_maxdivision_api_url="https://api.nexon.co.kr/fifaonline4/v1.0/users/{}/maxdivision"
    result={"accessId": "", "nickname":"","level":"","rank":"","autoRank":""}
    print(nickName)
    try:
        nick_name_response = requests.get(fifa4_nick_name_api_url.format(nickName), headers=header)
        if nick_name_response.status_code == 200:
   
            #accessId	String	유저 고유 식별자 
            #nickname	String	유저 닉네임 
            #level	Integer	유저 레벨 
     
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
            else:
                raise HTTPException(status_code=maxdivision_response.status_code, detail=maxdivision_response.text)
        else:
            raise HTTPException(status_code=nick_name_response.status_code, detail=nick_name_response.text)
    except requests.RequestException as error:
        raise HTTPException(status_code=500, detail=str(error))

    return result
"""
