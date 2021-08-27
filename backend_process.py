# -*-coding:utf-8-*-
##############################################################################
#
#       [ BackEnd Processing Program ]
#   수정일 : 2021-08-26
#   작성자 : 최현식(chgy2131@naver.com)
#   변경점 (해야할거)
#        - 파이어스토어 스케쥴 확인 부분 추가
#        - 스마트홈 기기 제어 부분 추가
#        - 각 기기(안드로이드,웹오에스)로 부터 받은 스케쥴값을 파이어베이스에 추가하는 기능 구현해야함.
#        - 각 MQTT 함수는 독립적인 connection을 가집니다.
#        - MQTT 메시지 publish(전송)시 매 시점마다 채널을 열고/닫습니다.
#        - MQTT 메세지 consume(수신)시에 사용하는 채널을 분리합니다.
#        - 스케쥴 type이 once인 데이터는 실행후 삭제한다.
#		 - data.smarthome(clone)을 consume(수신)하여 작업 체크.
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

debug_msg = True

slack_token = "xoxb-2362622259573-2358980968998-mSTtdyrrEoh7fNjXdYb7wYOX"
firebase_key_path = './firebase-python-sdk-key/threeamericano-firebase-adminsdk-ejh8q-d74c5b0c68.json'
firebase_project_name = 'threeamericano'
json_file_path = "./realtimedb.json"
mode_file_path = "./smarthome_mode"


def receive_test_test(json_data):
    print("recive test producer and command!")


def receive_server_alert(json_data):
    print("receive server alert msg!")


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

    # MQTT를 통해 '이름값 반환' 메세지
    mqtt_publish('webos.car.info', message)


def receive_android_signup(json_data):
    # JSON 데이터 유효성 검사 (KEY 확인)
    try:
        json_key_is_there(json_data, ['UID', 'name'])
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
    mqtt_publish('webos.android.info', message)


##############################################################################
#
# 선언 및 정의 (일반함수)
#
##############################################################################
def print_debug(message):
    global debug_msg
    if debug_msg:
        print(message)

def alert_error(routing_key, message):
    print(message)
    try:
        sl.slack_post_message('#server', message)
    except Exception as e:
        print("========== SLACK 메세지 전송에 실패했습니다. ========== %r" % e)
    try:
        mqtt_publish('data.error.info', message)
    except Exception as e:
        print("========== MQTT로 에러메세지 전송에 실패했습니다.  ========== %r" % e)
        return False


def write_mode_state(file_path, now_state):
    mode_file = open(file_path, "wt")
    mode_file.write(str(now_state))
    mode_file.close()
    time.sleep(5)


def read_jsonfile(file_path):
    with open(file_path, "rt", encoding='CP949', errors='ignore') as json_file:
        dict_data = json.load(json_file)
        return dict_data


def json_key_is_there(json_data, key_list):
    try:
        for key in key_list:
            temp = json_data[key]
    except Exception as e:
        raise(e)


def dict_realtimedb_for_smarthome(dict_data):
    # RealTimeDB를 통해 확인한 스마트홈의 가전들의 현재상태를, 각각의 변수로 변환해주는 함수
    smarthome = dict_data['smarthome']
    mode = smarthome['mode']
    status = smarthome['status']

    aircon_enable = status[0:1]
    aircon_fan = status[1:2]
    light_enable = status[2:3]
    light_brightness = status[3:4]
    light_color = status[4:5]
    light_mod = status[5:6]
    window_enable = status[6:7]
    gas_enable = status[7:8]

    return mode, aircon_enable, aircon_fan, light_enable, light_brightness, light_color, light_mod, window_enable, gas_enable


def dict_for_smarthome(dict_data):
    # 스케쥴 DB에서 가져온 dict 데이터를, 스마트홈 가전제어 프로토콜에 사용하기 위한 변수로 변환해주는 함수
    if str(type(dict_data)) != "<class 'dict'>":
        raise Exception("인자값이 딕셔너리 클래스가 아닙니다.")

    do_type = dict_data['type']

    try:
        if dict_data['Device_aircon'][0]:
            aircon_enable = '1'
        else:
            aircon_enable = '0'
    except Exception as e:
        aircon_enable = '2'
    try:
        aircon_fan = str(dict_data['Device_aircon'][1])
    except Exception as e:
        aircon_fan = '0'

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

    return do_type, aircon_enable, aircon_fan, light_enable, light_brightness, light_color, light_mod, window_enable, gas_enable


def send_control_smarthome(aircon_enable, aircon_fan,
                           light_enable, light_brightness, light_color, light_mod,
                           window_enable, gas_enable):
    message = aircon_enable + aircon_fan + light_enable + light_brightness + light_color + light_mod + window_enable + gas_enable

    # MQTT를 통해 '스마트홈 가전제어' 메세지 전송
    mqtt_publish('webos.smarthome.info', message)


def read_firestore(collection_name):
    # Firesotre Update 되었을때만 가져오는 함수가 있는지 확인
    schedule_ref = db.collection(collection_name)
    docs = schedule_ref.stream()
    '''
    for doc in docs:
        print(u'{} => {}'.format(doc.id, doc.to_dict()))
    '''
    return docs


def delete_schedule(document_name):
    #파이어베이스에 해당 문서 삭제
    db.collection(u'schedule_mode').document(document_name).delete()


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
    temp = (dict_data['type'])

    if dict_data['type'] == 'once':
        temp = (dict_data['Active_date'])
    elif dict_data['type'] == 'repet':
        temp = (dict_data['Enabled'])
        temp = (dict_data['Daysofweek'])
        temp = (dict_data['Start_time'])
    elif dict_data['type'] == 'mode':
        pass
    else:
        raise Exception("해당 문서에 'type'값에 형식이 잘못되었습니다. 실행함수:check_schedule_right. ")


def check_schedule_now(dict_data):
    check_state = False
    if dict_data['type'] == 'once':
        # 일회성 로직인 경우
        active_time = int(re.sub(r'[^0-9]', '', str(dict_data['Active_date'])[0:16]))
        now_time = int(time.strftime("%Y%m%d%H%M", time.localtime(time.time())))

        # 확인 조건문
        if (active_time - 1) <= now_time <= (active_time + 1):
            check_state = True
    elif dict_data['type'] == 'repet':
        # 실행해야되는건지 일단 확인
        time.sleep(0.0001)
        if not dict_data['Enabled']:
            return False

        # 주기적 로직인 경우
        now_dayoftheweek = dict_data['Daysofweek'][int(time.strftime("%w", time.localtime(time.time())))]  # 동작 요일 확인
        if not now_dayoftheweek:
            return False

        # 일단 STR을 INT형으로 바꾼후 비교문 연산
        now_time = int(time.strftime("%H%M", time.localtime(time.time())))
        start_time = int(dict_data['Start_time'])

        time.sleep(0.0001)
        if (start_time - 1 <= now_time) and (now_time <= start_time + 1):
            check_state = True
        else:
            check_state = False
    elif dict_data['type'] == 'mode':  #모드는 서버에서 직접 실행되지 않음
        check_state = False
    else:
        raise Exception("해당 문서에 'type'값에 형식이 잘못되었습니다. 실행함수:check_schedule_now. ")

    return check_state


def on_mqtt_message(channel, method_frame, header_frame, body):
    print("[R] ecive MQTT Message")

    #상수(int)형 메세지인지 확인 (안받아요~)
    if str(type(body)) == 'int':
        alert_error('data.error.warning',
                    "WARNING : 상수형 데이터가 들어왔습니다. 이를 무시합니다. *값 : " + str(body))

    # 메세지 내용을 JSON 형태로 정제
    try:
        body_decode = body.decode()
        json_data = json.loads(body_decode)
        # iterator = iter(json_data)
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
    if globals_var.find('receive_' + function_name) == -1:
        alert_error('webos.' + json_data['Producer'] + '.error',
                    "WARNING : 처리함수가 없는 데이터가 들어왔습니다. 이를 무시합니다. *로딩함수명 : " + str('receive_' + function_name))
        return False

    # 해당 메세지 처리 함수로 연결
    try:
        globals()[str('receive_' + function_name)](json_data)
    except Exception as e:
        alert_error('webos.' + json_data['Producer'] + '.error',
                    "ERROR : 처리함수 실행중 에러가 발생했습니다. 확인이 필요합니다. *오류명 : " + str(e))
        return False


def on_mqtt_smarthome(channel, method_frame, header_frame, body):
    try:
        body_decode = body.decode()
    except Exception as e:
        print("no~")

    #데이터 형식 확인 (9글자)
    if len(body_decode) != 9:
        return False

    #사용할 데이터 정제
    status = body_decode

    mode = status[0:1]
    aircon_enable = status[1:2]
    aircon_fan = status[2:3]
    light_enable = status[3:4]
    light_brightness = status[4:5]
    light_color = status[5:6]
    light_mod = status[6:7]
    window_enable = status[7:8]
    gas_enable = status[8:9]

    #기대상태 변수에 각 정보들을 모두 저장
    print(body_decode)

    #아래는 단순 테스트용, 나중에 다른함수나 메인쪽으로 돌리셈;
    write_mode_state(mode_file_path, mode)


def thread_consume_queue():
    # RabbitMQ 연결 및 정보등록
    rb2 = rabbitmq_clinet.RabbitmqClient('211.179.42.130', 5672, 'rabbit', 'MQ321')
    conn = rb2.connect_server()
    time.sleep(0.01)

    # RabbitMQ 채널 생성 및 구독 정보 입력
    consume_channel = rabbitmq_clinet.RabbitmqChannel(conn)  # webos.server 큐 구독용 채널
    consume_channel.open_channel()
    time.sleep(0.01)
    consume_channel.consume_setting('webos.server', on_mqtt_message)
    consume_channel.consume_starting()


def thread_consume_smarthome():
    # RabbitMQ 연결 및 정보등록
    rb3 = rabbitmq_clinet.RabbitmqClient('211.179.42.130', 5672, 'rabbit', 'MQ321')
    conn = rb3.connect_server()
    time.sleep(0.01)

    # RabbitMQ 채널 생성 및 구독 정보 입력
    consume_channel = rabbitmq_clinet.RabbitmqChannel(conn)  # webos.server 큐 구독용 채널
    consume_channel.open_channel()
    time.sleep(0.01)
    consume_channel.consume_setting('data.smarthome', on_mqtt_smarthome)
    consume_channel.consume_starting()


def mqtt_publish(routing_key, message):
    # 커넥션 생성
    rb = rabbitmq_clinet.RabbitmqClient('211.179.42.130', 5672, 'rabbit', 'MQ321')
    mqtt_conn = rb.connect_server()
    time.sleep(0.01)

    # 채널개설
    publish_channel = rabbitmq_clinet.RabbitmqChannel(mqtt_conn)  # 백엔드 처리용 MQTT 채널
    publish_channel.open_channel()
    time.sleep(0.01)

    # 메세지 전달
    try:
        publish_channel.publish_exchange('webos.topic', routing_key, str(message))
    except Exception as e:
        print("========== MQTT 메세지 전송에 실패했습니다.  ========== %r" % e)
        return False

    # 채널 및 커넥션 닫기
    publish_channel.close_channel()
    time.sleep(0.01)
    rb.disconnect_server()
    time.sleep(0.01)


##############################################################################
#
# 초기설정 (Init)
#
##############################################################################

# Slack Bot 개체 생성하기
print("[init] Slack Bot")
sl = slack.SlackBot(token=slack_token)
time.sleep(0.01)

# 파이어베이스 프로젝트에 접속하기
print("[init] FireStore")
cred = credentials.Certificate(firebase_key_path)
firebase_admin.initialize_app(cred, {
    'projectID': firebase_project_name,
})
db = firestore.client()
time.sleep(0.01)

# RabbitMQ 구독 진행 (쓰레드 실행)
print("[init] RabbitMQ Thread (webos.server)")
t = threading.Thread(target=thread_consume_queue, daemon=True)  # webos.server
t.start()
time.sleep(4)

print("[init] RabbitMQ Thread (data.smarthome)")
t2 = threading.Thread(target=thread_consume_smarthome, daemon=True)  # data.smarthome
t2.start()
time.sleep(4)

# write_mode_state(mode_file_path, "fuckyou")
##############################################################################
#
# 반복 실행
#
##############################################################################
print("[init] backend_process.py 가동을 시작합니다.")
while True:  # 메인루프에 전체적으로 딜레이시간을 주는걸로? (참고로 스마트홈 업데이트 갱신주기가 1분)
    # RealTime DB 값 불러오기
    print_debug("[A] Load RealTime DB JSON")
    try:
        rtdb_dict_data = read_jsonfile(json_file_path)  # 정안되면 이걸 json이 아닌 config로 만들어..?
        #print(rtdb_dict_data)
    except Exception as e:
        alert_error("data.error.error",
                    "ERROR : RealTimeDB.JSON을 불러오는 중에 오류가 발생하였습니다. 확인이 필요합니다. *오류명 : %r" % str(e))
		
    # FireStore Schedule 값 불러오기
    print_debug("[A] Load FireStore Schedule")
    try:
        # FireStore의 schedule_mode 컬렉션 불러오기
        print_debug(" ┗[1] Load 'Schedule_mode' collection")
        schedule_query = read_firestore('schedule_mode')

        # 각 문서(doc)별로 내용 분석
        print_debug(" ┗[2] schedule to dict")
        for doc in schedule_query:
            schedule_dict = doc.to_dict()
            try:
                # DB에 저장되어있던 스케쥴 형식이 정상적인 형식인지 확인
                print_debug("   ┗[1] check schedule right")
                check_schedule_right(schedule_dict)
            except Exception as e:
                alert_error("data.error.error",
                            "WARNING : FireStore DB에 형식이 잘못된 데이터가 있습니다. 확인이 필요합니다. *문서ID : " +
                            str(doc.id) + " / *오류명 : " + str(e))
                continue

            # 현재 실행해야 하는 스케쥴인지 확인
            print_debug("   ┗[2] check run this time")
            if check_schedule_now(schedule_dict):
                # 실시간DB의 값을 '스마트홈 프로토콜 형식'으로 변환
                om, o1, o2, o3, o4, o5, o6, o7, o8 = dict_realtimedb_for_smarthome(rtdb_dict_data)

                # '스마트홈 프로토콜 형식'으로 명령 생성
                mm, m1, m2, m3, m4, m5, m6, m7, m8 = dict_for_smarthome(schedule_dict)

                # 스케쥴값과 실시간DB값을 비교하여, 실행해야 하는 명령만 명령으로 확정
                print_debug("{0} {1} {2} {3} {4} {5} {6} {7}".format(o1,o2,o3,o4,o5,o6,o7,o8))
                print_debug("{0} {1} {2} {3} {4} {5} {6} {7}".format(m1,m2,m3,m4,m5,m6,m7,m8))
                flag_sendmsg = False
                if m1 != o1 and m1 != '2':  # on/off값이 기존과 다르고, 현행유지 상태가 아니라면 명령을 새로 내린다.
                    flag_sendmsg = True
                elif m1 == '1' and m2 != o2:  # 밝기제어값이 다른경우
                    flag_sendmsg = True

                if m3 != o3 and m3 != '2':
                    flag_sendmsg = True
                elif m3 == '1' and (m4 != o4 or m5 != o5 or m6 != o7):
                    flag_sendmsg = True

                if m7 != o7 and m7 != '2':
                    flag_sendmsg = True
                if m8 != o8 and m8 != '2':
                    flag_sendmsg = True

                # 새로 진행해야할 명령이 있따면, 해당명령을 '스마트홈 큐'로 전달
                # print("flag : %r" % str(flag_sendmsg))
                if flag_sendmsg:
                    print("   ┗[3] send control msg to smarthome")
                    send_control_smarthome(m1, m2, m3, m4, m5, m6, m7, m8)
                    print("[X] send to smarthome queue")
                # 명령 전달이후 once 인 메세지는 스케쥴에서 삭제진행 ㄱㄱ
                if mm == 'once':
                    print("   ┗[4] delete schedule (cuz it is 'type: once')")
                    delete_schedule(doc.id)

    except Exception as e:
        alert_error("data.error.error",
                    "ERROR : FireStore Schedule 값을 처리하는 중 오류가 발생하였습니다. 확인이 필요합니다. *오류명 : %r" % str(e))
    # 또 어떤 로직이 이곳에 오게될것인가~

    # 동작대기
    time.sleep(20)

