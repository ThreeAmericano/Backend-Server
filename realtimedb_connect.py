#-*-coding:utf-8-*-
##############################################################################
#
#       [ RealTime Database connect Program ]
#   수정일 : 2021-09-09
#   작성자 : 최현식(chgy2131@naver.com)
#   변경점
#           - 더 이상 smarthome에 모드를 업데이트 하지 않음.
#           - RealTimeDB의 Smarthome에 리스너를 적용하여, 변경점이 생길때만 값읽기 진행
#           - openWeatherAPI 갱신주기 15분으로 수정
#           - 변경점 발생시에만 RealTime DB에 Write를 진행하도록 수정
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
weather_get_interval = 900 #sec (매 15분)
weather_get_latest = time.time() - weather_get_interval


def alert_error(message):
    print(message)
    sl.slack_post_message('#server', message)


def write_jsonfile(file_path, dict_data):
    with codecs.open(file_path, 'w', encoding='CP949') as outfile:
        json.dump(dict_data, outfile, indent=4, ensure_ascii=False)


def listen_callback(args):
    try:
        print("[info] RTDB의 smarthome 가전상태에 변화가 감지되어 갱신합니다.")
        ddata = rtdb.get()
        write_jsonfile(json_file_path, ddata)
        listen_latest_time = time.time()
    except Exception as e:
        alert_error('ERROR : RealTime DB에서 데이터를 불러오는 중 오류가 발생하였습니다. 확인이 필요합니다.')


mode_file_path = "./smarthome_mode"
def read_modefile(file_path):
    mode_file = open(file_path, "r")
    mode_data = mode_file.readline()
    mode_file.close()
    return mode_data


# Slack Bot 개체 생성하기
sl = slack.SlackBot(token=slack_bot_token)

# 파이어베이스 RealTime DB 연결 및 개체생성
cred = credentials.Certificate(firebase_key_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': firebase_realtimedb_url
})
rtdb = db.reference()

# 파이어베이스 RealTime DB측 smarthome을 모니터링하여 자동으로 업데이트하는 것 생성
rtdb_smarthome = db.reference().child("smarthome")
rtdb_smarthome.listen(listen_callback)

# OpenWeatherAPI 개체 생성하기
ow = openweathermap_api.OpenWeatherAPI(service_key=openweathermap_service_key)

##############################################################################
#
# 반복 실행
#
##############################################################################
try:
    while True:
        time.sleep(1)
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

                # 파이어베이스 RealTime DB에 값 업데이트하기
                try:
                    # OpenWeather API 값 업데이트
                    for key in ow_dict:
                        rtdb.child("sensor").child("openweather").update({key: ow_dict[key]})

                    # RTDB의 최신값 불러와서 파일로 저장하기
                except Exception as e:
                    alert_error("ERROR : FireBase RealTime DB 사용 중 오류가 발생했습니다. 확인이 필요합니다. *오류명 : %r" % str(e))

            except Exception as e:
                alert_error("ERROR : OpenWeatherMap API를 통해 값을 요청하던 중 오류가 발생했습니다. 확인이 필요합니다. *오류명 : %r" % str(e))\

except KeyboardInterrupt:
    quit()
