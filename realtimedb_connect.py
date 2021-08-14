#-*-coding:utf-8-*-
##############################################################################
#
#       [ RealTime Database connect Program ]
#   수정일 : 2021-08-15
#   작성자 : 최현식(chgy2131@naver.com)
#   변경점 (해야할거)
#        - 최초작성
#
##############################################################################
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from module.weather_api import openweathermap_api
from module.slack import slack
import time
import json

slack_bot_token = "xoxb-2362622259573-2358980968998-mSTtdyrrEoh7fNjXdYb7wYOX"
json_file_path = "./realtimedb.json"
firebase_key_path = './firebase-python-sdk-key/threeamericano-firebase-adminsdk-ejh8q-d74c5b0c68.json'
firebase_realtimedb_url = 'https://threeamericano-default-rtdb.firebaseio.com/'
openweathermap_service_key = "c7446d3b017961049805343e08347b43"


def alert_error(message):
    print(message)
    sl.slack_post_message('#server', message)


def write_jsonfile(file_path, dict_data):
    with open(json_file_path, 'w') as outfile:
        json.dump(dict_data, outfile, indent=4, ensure_ascii=False)


# Slack Bot 개체 생성하기
sl = slack.SlackBot(token=slack_bot_token)

# 파이어베이스 RealTime DB 연결
cred = credentials.Certificate(firebase_key_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': firebase_realtimedb_url
})

# OpenWeatherAPI 개체 생성하기
ow = openweathermap_api.OpenWeatherAPI(service_key=openweathermap_service_key)

##############################################################################
#
# 반복 실행
#
##############################################################################

# 날씨API를 통해 값 가져오기
ow.update_now_auto("Seoul")
ow_dict = ow.getter_dict()
print(ow_dict)

print("===================================")
# 파이어베이스 RealTime DB에 값 업데이트하기
rtdb = db.reference()
for key in ow_dict:
    rtdb.child("sensor").child("openweather").update({key: ow_dict[key]})

ddata = rtdb.get()
write_jsonfile(json_file_path, ddata)

