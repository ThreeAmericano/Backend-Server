#-*-coding:utf-8-*-
##############################################################################
#
#       [ BackEnd Processing Program ]
#   수정일 : 2021-08-18
#   작성자 : 최현식(chgy2131@naver.com)
#   변경점 (해야할거)
#        - 파이어스토어 스케쥴 확인 부분 추가
#        - 스마트홈 기기 제어 부분 추가
#        - 각 기기(안드로이드,웹오에스)로 부터 받은 스케쥴값을 파이어베이스에 추가하는 기능 구현해야함.
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
import re
from firebase_admin import credentials
from firebase_admin import firestore
from module.rabbitmq import rabbitmq_clinet
from module.slack import slack

slack_token = "xoxb-2362622259573-2358980968998-mSTtdyrrEoh7fNjXdYb7wYOX"
firebase_key_path = './firebase-python-sdk-key/threeamericano-firebase-adminsdk-ejh8q-d74c5b0c68.json'
firebase_project_name = 'threeamericano'
json_file_path = "./realtimedb.json"
#mqtt_server_ip = '211.179.42.130'
#mqtt_server_port = 5672
#mqtt_server_id = 'rabbit'
#mqtt_server_pw = 'MQ321'


def receive_car_signup(json_data):
    # JSON 데이터 유효성 검사 (KEY 확인)
    try:
        json_key_is_there(json_data, ['UID', 'name'])
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
    be_channel.publish_exchange('webos.topic', 'webos.car.info', message)


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


def read_jsonfile(file_path):
    with open(file_path, "r") as json_file:
        dict_data = str(json.load(json_file))
        return dict_data


def json_key_is_there(json_data, key_list):
    for key in key_list:
        temp = json_data[key]


def dict_for_smarthome(dict_data):
    # 스케쥴 DB에서 가져온 dict 데이터를, 스마트홈 가전제어 프로토콜에 사용하기 위한 변수로 변환해주는 함수
    try:
        if dict_data['Device_aircon'][0]:
            aircon_enable = '1'
        else:
            aircon_enable = '0'
    except Exception as e:
        aircon_enable = '2'
    try:
        aircon_power = str(dict_data['Device_aircon'][1])
    except Exception as e:
        aircon_power = '0'

    try:
        if dict_data['Device_light'][0]:
            light_enable = '1'
        else:
            light_enable = '0'
    except Exception as e:
        light_enable = '2'
    try:
        light_brightness = str(dict_data['Device_light'][1])
    except Exception as e:
        light_brightness = '9'
    try:
        light_color = str(dict_data['Device_light'][2])
    except Exception as e:
        light_color = '0'
    try:
        light_mod = str(dict_data['Device_light'][3])
    except Exception as e:
        light_mod = '0'

    try:
        if dict_data['Device_window'][0]:
            window_enable = '1'
        else:
            window_enable = '0'
    except Exception as e:
        window_enable = '2'
    try:
        if dict_data['Device_gas'][0]:
            gas_enable = '1'
        else:
            gas_enable = '0'
    except Exception as e:
        gas_enable = '2'

    return aircon_enable, aircon_power, light_enable, light_brightness, light_color, light_mod, window_enable, gas_enable


def send_control_smarthome(aircon_enable, aircon_power,
                           light_enable, light_brightness, light_color, light_mod,
                           window_enable, gas_enable):
    message = aircon_enable + aircon_power + light_enable + light_brightness + light_color + light_mod + window_enable + gas_enable

    # MQTT를 통해 '스마트홈 가전제어' 메세지 전송
    be_channel.publish_exchange('webos.topic', 'webos.smarthome.info', message)


def read_firestore(collection_name):
    # Firesotre Update 되었을때만 가져오는 함수가 있는지 확인
    schedule_ref = db.collection(collection_name)
    docs = schedule_ref.stream()
    '''
    for doc in docs:
        print(u'{} => {}'.format(doc.id, doc.to_dict()))
    '''
    return docs


def update_schedule(collection_name, doc_title, dict_data):
    # 파이어베이스에 업로드하기 전, 데이터 무결성 검사
    check_schedule_right(dict_data)

    # 파이어베이스에 데이터 업로드
    doc_ref = db.collection(u'schedule_mode').document(doc_title)
    doc_ref.set(dict_data)


def check_schedule_right(dict_data):
    if str(type(dict_data)) != "<class 'dict'>":
        raise Exception("인자값이 딕셔너리 클래스가 아닙니다.")

    temp = (dict_data['UID'])
    temp = (dict_data['Enabled'])
    temp = (dict_data['One_time'])

    if dict_data['One_time'] == True:
        temp = (dict_data['Active_date'])
    elif dict_data['One_time'] == False:
        temp = (dict_data['Daysofweek'])
        temp = (dict_data['Start_time'])
        temp = (dict_data['End_time'])
    else:
        raise Exception("해당 문서에 'One_time'값이 bool형식이 아닙니다.")


def check_schedule_now(dict_data):
    if not dict_data['Enabled']:
        return False

    check_state = False

    if dict_data['One_time']:
        # 일회성 로직인 경우
        active_time = int(re.sub(r'[^0-9]', '', str(dict_data['Active_date'])[0:16]))
        now_time = int(time.strftime("%Y%m%d%H%M", time.localtime(time.time())))

        # 확인 조건문
        if (active_time - 1) <= now_time <= (active_time + 1):
            check_state = True
    else:
        # 주기적 로직인 경우
        now_dayoftheweek = dict_data['Daysofweek'][int(time.strftime("%w", time.localtime(time.time())))] # 동작 요일 확인
        if not now_dayoftheweek:
            return False

        # 일단 STR을 INT형으로 바꾼다음에 연산해야함.
        now_time = int(time.strftime("%H%M", time.localtime(time.time())))
        start_time = int(dict_data['Start_time'])
        end_time = int(dict_data['End_time'])
        check_state = False

        # 확인 조건문
        if (start_time < now_time) and (now_time < end_time):
            # 현재시간이 시작시간과 끝시간 사이에 위치한 경우
            check_state = True
        elif end_time < start_time:
            # 동작시간이 자정을 넘어서까지 있을때
            if start_time < now_time:
                # 아직 자정을 넘지 않은 경우
                check_state = True
            elif now_time < end_time:
                # 자정을 넘었지만 아직 종료시간이 아닌 경우
                check_state = True
            else:
                check_state = False
        else:
            check_state = False

    return check_state


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
    if globals_var.find('receive_'+function_name) == -1:
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


##############################################################################
#
# 초기설정 (Init)
#
##############################################################################

# Slack Bot 개체 생성하기
sl = slack.SlackBot(token=slack_token)

# 파이어베이스 프로젝트에 접속하기
cred = credentials.Certificate(firebase_key_path)
firebase_admin.initialize_app(cred, {
    'projectID': firebase_project_name,
})
db = firestore.client()

# RabbitMQ 연결 및 정보등록
#rb = rabbitmq_clinet.RabbitmqClient(mqtt_server_ip, mqtt_server_port, mqtt_server_id, mqtt_server_pw)
rb = rabbitmq_clinet.RabbitmqClient('211.179.42.130', 5672, 'rabbit', 'MQ321')
mqtt_conn = rb.connect_server()

be_channel = rabbitmq_clinet.RabbitmqChannel(mqtt_conn) # 백엔드 처리용 MQTT 채널
be_channel.open_channel()
be_channel.consume_setting('webos.server', on_mqtt_message)

# RabbitMQ 실제 실행구문 (쓰레드 실행)
t = threading.Thread(target=be_channel.consume_starting, daemon=True)
t.start()


##############################################################################
#
# 반복 실행
#
##############################################################################
while True:
    # RealTime DB 값 불러오기
    try:
        rtdb_dict_data = read_jsonfile(json_file_path)
        time.sleep(10)
    except Exception as e:
        alert_error("data.error.error",
                    "ERROR : RealTimeDB.JSON을 불러오는 중에 오류가 발생하였습니다. 확인이 필요합니다. *오류명 : %r" % str(e))

    # FireStore Schedule 값 불러오기
    try:
        schedule_query = read_firestore('schedule_mode')
        for doc in schedule_query:
            schedule_dict = doc.to_dict()
            try:
                print("[%r]" % str(doc.id))
                check_schedule_right(schedule_dict)
            except Exception as e:
                alert_error("data.error.error",
                            "WARNING : FireStore DB에 형식이 잘못된 데이터가 있습니다. 확인이 필요합니다. *문서ID : " +
                            str(doc.id) + " / *오류명 : " + str(e))
                continue

            # 현재 실행해야 하는 스케쥴인지 확인
            print(check_schedule_now(schedule_dict))
            if check_schedule_now(schedule_dict):
                print("<---------------->")
                m1, m2, m3, m4, m5, m6, m7, m8 = dict_for_smarthome(schedule_dict)
                send_control_smarthome(m1, m2, m3, m4, m5, m6, m7, m8)
                print("<---------------->")

    except Exception as e:
        alert_error("data.error.error",
                    "ERROR : FireStore Schedule 값을 처리하는 중 오류가 발생하였습니다. 확인이 필요합니다. *오류명 : %r" % str(e))

    # 또 어떤 로직이 이곳에 오게될것인가~

