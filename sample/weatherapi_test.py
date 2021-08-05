#-*-coding:utf-8-*-
#위 구문은 한글처리를 위해 필수임.
#
#아래는 동작링크예시.
#http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst?serviceKey=fF5OJkqdLH%2BOGt4%2F3F0FtaLc%2B4GsfqE%2BNxyg6iTAAl3NeK8jTGT26iCHraMiKTY%2FfXyHfox2azdPtitSo4SoXw%3D%3D&numOfRows=10&pageNo=1&base_date=20210803&base_time=0600&nx=55&ny=127
import urllib.request
import json
import datetime

# API 요청 REST 값 설정
vilage_weather_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"

service_key = "fF5OJkqdLH%2BOGt4%2F3F0FtaLc%2B4GsfqE%2BNxyg6iTAAl3NeK8jTGT26iCHraMiKTY%2FfXyHfox2azdPtitSo4SoXw%3D%3D"

numofRows="10"
pageNo="1"

today = datetime.datetime.today()
base_date = today.strftime("%Y%m%d") # "20200214" == 기준 날짜
base_time = "0800" # 날씨 값

nx = "60"
ny = "128"

payload = "?serviceKey=" + service_key + "&" +\
    "numofRows=" + numofRows + "&" +\
    "pageNo=" + pageNo + "&" +\
    "dataType=json" + "&" +\
    "base_date=" + base_date + "&" +\
    "base_time=" + base_time + "&" +\
    "nx=" + nx + "&" +\
    "ny=" + ny

# 값 요청
url_total = vilage_weather_url + payload
print(url_total)
req = urllib.request.urlopen(url_total)
res = req.readline()
print(res)

# 받은 값 JSON 형태로 정제
items = json.loads(res)
print(" - DATA TYPE : %r" % items['response']['body']['dataType'])

for item in items['response']['body']['items']['item']:
    print(item['category'])
    print(item['obsrValue'])
    print("\n")
