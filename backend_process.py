#-*-coding:utf-8-*-
##############################################################################
#
#       [ BackEnd Processing Program ]
#   수정일 : 2021-08-13
#   작성자 : 최현식(chgy2131@naver.com)
#   변경점 (해야할거)
#        - 스마트홈 기기 제어 부분 추가해야함
#        - 날씨API를 통해 ini 파일을 만들어서 전달하는 프로그램
#        - RealTime DB 값을 ini 파일을 통해 가져오는 로직
#        -
#
##############################################################################


##############################################################################
#
# 선언 및 정의 (모듈 로드 및 MQTT명령 처리)
#
##############################################################################
import time
import threading
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from module.rabbitmq import rabbitmq_clinet
from module.weather_api import weather_api
from module.slack import slack

slack_token = 0
firebase_key_path = 0
mqtt_server_ip = 0
mqtt_server_port = 0
mqtt_server_id = 0
mqtt_server_pw = 0


def receive_car_signup(json_data):
    # JSON 데이터 유효성 검사 (KEY 확인)
    try:
        json_key_is_there(json_data,['UID', 'name'])
    except Exception as e:
        alert_error('webos.car.error',
				"ERROR : 도착한 JSON 데이터의 형식이 기존 규약과 상이합니다. 확인이 필요합니다. *오류내용 : " + str(e))
        return False

    # 파이어베이스에 신규가입회원 데이터 추가
    doc_ref = db.collection(u'user_account').document(json_data['UID'])
    doc_ref.set({
        u'name': json_data['name']
    })


def receive_car_signin(json_data):
    # JSON 데이터 유효성 검사 (KEY 확인)
    try:
        json_key_is_there(json_data, ['UID'])
    except Exception as e:
        alert_error('webos.car.error',
                    "ERROR : 도착한 JSON 데이터의 형식이 기존 규약과 상이합니다. 확인이 필요합니다. *오류내용 : " + str(e))
        return False

    # 파이어베이스에서 해당 회원(UID)의 이름을 가져옴
    users_ref = db.collection(u'user_account').document(json_data['UID'])
    docs = users_ref.get()

    # JSON 형태로 변환
    if docs.exists:
        # print(f'Document data: {docs.to_dict()}')
        docs_json_data = docs.to_dict()
        docs_json_data['Producer'] = "server"
        docs_json_data['command'] = "return_name"
        message = json.dumps(docs_json_data, ensure_ascii=False)
    else:
        alert_error('webos.car.error',
                    "ERROR : UID에 해당하는 유저 정보가 없습니다. 확인이 필요합니다.")
        return False

    # MQTT를 통해 '이름값 반환' 메세지 전송
    rb.publish_exchange('webos.topic', 'webos.car.info', message)


def receive_android_signup(json_data):
    # JSON 데이터 유효성 검사 (KEY 확인)
    try:
        json_key_is_there(json_data,['UID', 'name'])
    except Exception as e:
        alert_error('webos.android.error',
                    "ERROR : 도착한 JSON 데이터의 형식이 기존 규약과 상이합니다. 확인이 필요합니다. *오류내용 : " + "KeyError." + str(e))
        return False

    # 파이어베이스에 신규가입회원 데이터 추가
    doc_ref = db.collection(u'user_account').document(json_data['UID'])
    doc_ref.set({
        u'name': json_data['name']
    })


def receive_android_signin(json_data):
    # JSON 데이터 유효성 검사 (KEY 확인)
    try:
        json_key_is_there(json_data, ['UID'])
    except Exception as e:
        alert_error('webos.android.error',
                    "ERROR : 도착한 JSON 데이터의 형식이 기존 규약과 상이합니다. 확인이 필요합니다. *오류내용 : " + "KeyError." + str(e))
        return False

    # 파이어베이스에서 해당 회원(UID)의 이름을 가져옴
    users_ref = db.collection(u'user_account').document(json_data['UID'])
    docs = users_ref.get()

    # JSON 형태로 변환
    if docs.exists:
        # print(f'Document data: {docs.to_dict()}')
        docs_json_data = docs.to_dict()
        docs_json_data['Producer'] = "server"
        docs_json_data['command'] = "return_name"
        message = json.dumps(docs_json_data, ensure_ascii=False)
    else:
        alert_error('webos.android.error',
                    "ERROR : UID에 해당하는 유저 정보가 없습니다. 확인이 필요합니다.")
        return False

    # MQTT를 통해 '이름값 반환' 메세지 전송
    be_channel.publish_exchange('webos.topic', 'webos.android.info', message)


##############################################################################
#
# 선언 및 정의 (일반함수)
#
##############################################################################

def alert_error(routing_key, message):
    print(message)
    dict_msg = {"Producer": "server", "command": "alert", "msg": str(message)}
    json_dump = json.dumps(dict_msg, ensure_ascii=False)
    try:
        be_channel.publish_exchange('webos.topic', routing_key, json_dump)
        sl.slack_post_message('#server', message)
    except Exception as e:
        print("<><><> 에러메세지 전송에 실패했습니다. %r <><><>" % e)
        return False


def json_key_is_there(json_data, key_list):
    for key in key_list:
        temp = json_data[key]


def on_mqtt_message(channel, method_frame, header_frame, body):
    print("[ Recive Message from MQTT Queue ]")
    # 메세지 내용을 JSON 형태로 정제
    try:
        body_decode = body.decode()
        json_data = json.loads(body_decode)
        iterator = iter(json_data)
    except Exception as e:
        alert_error('data.error.warning',
                    "WARNING : JSON 형식이 아닌 데이터가 들어왔습니다. 이를 무시합니다. *오류내용 : " + str(e))
        return False

    # 기본 KEY값(Producer, command)이 있는지 확인
    try:
        json_key_is_there(json_data, ['Producer', 'command'])
    except KeyError:
        alert_error('data.error.warning',
                    "WARNING : 기본키가 없는 데이터가 들어왔습니다. 이를 무시합니다. *내용 : " + body_decode)
        return False

    # 해당 메세지를 처리할 수 있는 함수가 있는지 확인
    function_name = str(json_data['Producer']) + '_' + str(json_data['command'])
    globals_var = str(globals())
    if globals_var.find('receive_'+function_name) == -1 :
        alert_error('webos.'+json_data['Producer']+'.error',
                    "WARNING : 처리함수가 없는 데이터가 들어왔습니다. 이를 무시합니다. *로딩함수명 : " + str('receive_'+function_name))
        return False

    # 해당 메세지 처리 함수로 연결
    try:
        globals()[str('receive_'+function_name)](json_data)
    except Exception as e:
        alert_error('webos.'+json_data['Producer']+'.error',
                    "ERROR : 처리함수 실행중 에러가 발생했습니다. 확인이 필요합니다. *오류명 : " + str(e))
        return False


class WeatherAPI:
    weather_get_interval = 3600 # n초마다 작업진행
    weather_get_last_time = time.time() - weather_get_interval

    def check_timeing(self):
        now_interval = time.time() - self.weather_get_last_time
        if now_interval >= self.weather_get_interval:
            return True
        else:
            return False

    def get_weather(self, px, py):
        # 시간 경과 확인
        if self.check_timeing():
            # API를 통해 날씨정보를 받아옴 (return: JSON)
            try:
                weather_json = weather_api.getUltraSrtNcst(px, py)
                self.weather_get_last_time = time.time()
            except Exception as e:
                alert_error('data.error.error',
                            'ERROR : 날씨API로 부터 값을 받아오는 도중 에러가 발생했습니다. 확인이 필요합니다. *오류명 : ' + str(e))
                return False
            return weather_json
        else:
            return False

    def send_weather(self, send_json_data):
        # JSON 데이터가 왔는지 확인
        if send_json_data == False:
            print("json 데이터가 아니므로 종료")
            return False

        # 기존 메세지 소비
        try:
            method_frame = True
            while method_frame: # 새로운 메세지가 있는지 확인 (do-while)
                method_frame, header_frame, body = wa_channel_direct.basic_get(queue='data.weatherapi', auto_ack=True)
                if body == None: # Queue에 메세지가 없을 경우 예외처리
                    break
        except Exception as e :
            alert_error('data.error.error',
                        "ERROR : data.weatherapi 큐에 메세지를 소비하는 중에 에러가 발생했습니다. 확인이 필요합니다. *오류명 : " + str(e))
            time.sleep(0.01)

        # 새로운 날씨API 데이터 발행
        wa_channel.publish_exchange('webos.topic', 'data.weatherapi.info', send_json_data)


##############################################################################
#
# 초기설정 (Init)
#
##############################################################################

# Slack Bot 개체 생성하기
sl = slack.SlackBot(token="xoxb-2362622259573-2358980968998-mSTtdyrrEoh7fNjXdYb7wYOX")

# 파이어베이스 프로젝트에 접속하기
cred = credentials.Certificate('./firebase-python-sdk-key/threeamericano-firebase-adminsdk-ejh8q-d74c5b0c68.json')
firebase_admin.initialize_app(cred, {
    'projectID': 'threeamericano',
})
db = firestore.client()

# RabbitMQ 연결 및 정보등록
rb = rabbitmq_clinet.RabbitmqClient('211.179.42.130', 5672, 'rabbit', 'MQ321')
mqtt_conn = rb.connect_server()

wa_channel = rabbitmq_clinet.RabbitmqChannel(mqtt_conn) # 날씨API 갱신용 MQTT 채널
wa_channel_direct = wa_channel.open_channel()

be_channel = rabbitmq_clinet.RabbitmqChannel(mqtt_conn) # 백엔드 처리용 MQTT 채널
be_channel.open_channel()
be_channel.consume_setting('webos.server', on_mqtt_message)

# RabbitMQ 실제 실행구문 (쓰레드 실행)
t = threading.Thread(target=be_channel.consume_starting, daemon=True)
t.start()

# 날씨 API 개체 생성
wa = WeatherAPI()


##############################################################################
#
# 반복 실행
#
##############################################################################

while True:
    # 날씨 값 갱신 (날씨API)
    wa_json = wa.get_weather("60", "128")
    try:
        wa.send_weather(wa_json)
    except Exception as e:
        print(e)

    # 또 어떤 로직이 이곳에 오게될것인가~
