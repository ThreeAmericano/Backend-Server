#-*-coding:utf-8-*-

##############################################################################
#
#       [ BackEnd Processing Program ]
#   작성일 : 2021-08-10
#   작성자 : 최현식(chgy2131@naver.com)
#   변경점
#        - 최초작성
#
##############################################################################


##############################################################################
#
# 선언 및 정의 (모듈 로드 및 MQTT명령 처리)
#
##############################################################################
import threading
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from module.rabbitmq import rabbitmq_clinet
from module.weather_api import weather_api


def receive_android_signup(json_data):
    # JSON 데이터 유효성 검사 (KEY 확인)
    try:
        json_key_is_there(json_data,['UID', 'name'])
    except Exception as e:
        alert_error('webos.android.error', "ERROR : 도착한 JSON 데이터의 형식이 기존 규약과 상이합니다. 확인이 필요합니다. *오류내용 : " + str(e))
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
        alert_error('webos.android.error', "ERROR : 도착한 JSON 데이터의 형식이 기존 규약과 상이합니다. 확인이 필요합니다. *오류내용 : " + str(e))
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
        alert_error('webos.android.error', "ERROR : UID에 해당하는 유저 정보가 없습니다. 확인이 필요합니다.")
        return False

    # MQTT를 통해 '이름값 반환' 메세지 전송
    rb.publish_exchange('webos.topic', 'webos.android.info', message)


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
        rb.publish_exchange('webos.topic', routing_key, json_dump)
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
        alert_error('data.error.warning', "WARNING : JSON 형식이 아닌 데이터가 들어왔습니다. 이를 무시합니다. *오류내용 : " + str(e))
        return False

    # 기본 KEY값(Producer, command)이 있는지 확인
    try:
        json_key_is_there(json_data, ['Producer', 'command'])
    except KeyError:
        alert_error('data.error.warning', "WARNING : 기본키가 없는 데이터가 들어왔습니다. 이를 무시합니다. *내용 : " + body_decode)
        return False

    # 해당 메세지를 처리할 수 있는 함수가 있는지 확인
    function_name = str(json_data['Producer']) + '_' + str(json_data['command'])
    globals_var = str(globals())
    if globals_var.find('receive_'+function_name) == -1 :
        alert_error('webos.'+json_data['Producer']+'.error', "WARNING : 처리함수가 없는 데이터가 들어왔습니다. 이를 무시합니다. *로딩함수명 : " + str('receive_'+function_name))
        return False

    # 해당 메세지 처리 함수로 연결
    try:
        globals()[str('receive_'+function_name)](json_data)
    except Exception as e:
        alert_error('webos.'+json_data['Producer']+'.error', "ERROR : 처리함수 실행중 에러가 발생했습니다. 확인이 필요합니다. *오류명 : " + e)
        return False





##############################################################################
#
# 실제 실행구문
#
##############################################################################

# 파이어베이스 프로젝트에 접속하기
cred = credentials.Certificate('./firebase-python-sdk-key/threeamericano-firebase-adminsdk-ejh8q-d74c5b0c68.json')
firebase_admin.initialize_app(cred, {
	'projectID': 'threeamericano',
})
db = firestore.client()

# RabbitMQ 연결 및 정보등록
rb = rabbitmq_clinet.RabbitmqClient('211.179.42.130', 5672, 'rabbit', 'MQ321')
rb.connect_server()
rb.open_channel()
rb.consume_setting('webos.server', on_mqtt_message)

# RabbitMQ 실제 실행구문 (쓰레드 실행)
t = threading.Thread(target=rb.consume_starting, daemon=True)
t.start()


while True:
    a = True
