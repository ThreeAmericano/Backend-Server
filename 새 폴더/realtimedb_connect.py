#-*-coding:utf-8-*-
##############################################################################
#
#       [ RealTime Database connect Program ]
#   수정일 : 2021-08-25
#   작성자 : 최현식(chgy2131@naver.com)
#   변경점 (해야할거)
#			- read_mode_file 부분만집가서 합치면 됨
#
##############################################################################
import codecs
import time
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from module.weather_api import openweathermap_api
from module.slack import slack

slack_bot_token = "xoxb-2362622259573-2358980968998-mSTtdyrrEoh7fNjXdYb7wYOX"
json_file_path = "./realtimedb.json"
firebase_key_path = './firebase-python-sdk-key/threeamericano-firebase-adminsdk-ejh8q-d74c5b0c68.json'
firebase_realtimedb_url = 'https://threeamericano-default-rtdb.firebaseio.com/'
openweathermap_service_key = "c7446d3b017961049805343e08347b43"
weather_get_interval = 3600 #sec
weather_get_latest = time.time() - weather_get_interval


def alert_error(message):
    print(message)
    sl.slack_post_message('#server', message)


def write_jsonfile(file_path, dict_data):
    with codecs.open(json_file_path, 'w', encoding='CP949') as outfile:
        json.dump(dict_data, outfile, indent=4, ensure_ascii=False)


mode_file_path = "./smarthome_mode"
def read_modefile(file_path):
    mode_file = open(file_path, "r")
    mode_data = mode_file.readline()
    mode_file.close()
    return mode_data


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

while True:
    time.sleep(60)
    # 날씨API를 통해 값 가져오기
    now_interval = time.time() - weather_get_latest
    if now_interval < weather_get_interval:
        # print("날씨API 요청시간 : {0} / {1}".format(now_interval, weather_get_interval))
        pass
    else:
        try:
            ow.update_now_auto("Seoul")
            ow_dict = ow.getter_dict()
            weather_get_latest = time.time()
        except Exception as e:
            alert_error("ERROR : OpenWeatherMap API를 통해 값을 요청하던 중 오류가 발생했습니다. 확인이 필요합니다. *오류명 : %r" % str(e))

    # 파이어베이스 RealTime DB에 값 업데이트하기
    try:
        # OpenWeather API 값 업데이트
        rtdb = db.reference()
        for key in ow_dict:
            rtdb.child("sensor").child("openweather").update({key: ow_dict[key]})

        # SmartHome 동작 모드값 업데이트
        mode_state = read_modefile(mode_file_path)
        rtdb.child("smarthome").update({"mode":mode_state})

        # RTDB의 최신값 불러와서 파일로 저장하기
        ddata = rtdb.get()
        write_jsonfile(json_file_path, ddata)
    except Exception as e:
        alert_error("ERROR : FireBase RealTime DB 사용 중 오류가 발생했습니다. 확인이 필요합니다. *오류명 : %r" % str(e))


