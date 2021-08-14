#-*-coding:utf-8-*-
##############################################################################
#
#       [ RealTime Database connect Program ]
#   수정일 : 2021-08-14
#   작성자 : 최현식(chgy2131@naver.com)
#   변경점 (해야할거)
#        - 최초작성
#
##############################################################################
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from module.weather_api import openweathermap_api as ow
from module.slack import slack
import time
import json

json_file_path = "./realtimedb.json"


def alert_error(message):
    print(message)
    sl.slack_post_message('#server', message)


def write_jsonfile(file_path, dict_data):
    with open(json_file_path, 'w') as outfile:
        json.dump(dict_data, outfile, indent=4, ensure_ascii=False)


# Slack Bot 개체 생성하기
sl = slack.SlackBot(token="xoxb-2362622259573-2358980968998-mSTtdyrrEoh7fNjXdYb7wYOX")

# 파이어베이스 RealTime DB 연결
firebase_key_path = './firebase-python-sdk-key/threeamericano-firebase-adminsdk-ejh8q-d74c5b0c68.json'

cred = credentials.Certificate(firebase_key_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://threeamericano-default-rtdb.firebaseio.com/'
})


##############################################################################
#
# 반복 실행
#
##############################################################################

# 날씨API를 통해 값 가져오기
ow.getNowCity("Incheon")
ow_dict = ow.getterDict()
print(ow_dict)

print("===================================")
# 파이어베이스 RealTime DB에 값 업데이트하기
rtdb = db.reference()
for key in ow_dict:
    rtdb.child("sensor").child("openweather").update({key: ow_dict[key]})

ddata = rtdb.get()
write_jsonfile(json_file_path, ddata)

