# -*-coding:utf-8-*-
##############################################################################
#
#       [ BackEnd Processing Program ]
#   수정일 : 2021-09-22
#   작성자 : 최현식(chgy2131@naver.com)
#
#   변경점
#        - 파이어스토어 스케쥴 확인 부분 추가
#        - 스마트홈 기기 제어 부분 추가
#        - 각 MQTT 함수는 독립적인 connection을 가집니다.
#        - MQTT 메시지 publish(전송)시 매 시점마다 채널을 열고/닫습니다.
#        - MQTT 메세지 consume(수신)시에 사용하는 채널을 분리합니다.
#        - 파이어스토어 스케쥴 부분 구성 변경에 따른 관련 함수 수정
#        - 얼굴인식을 독립적인 프로세스로 진행함.
#        - 파이어스토어의 alarm, modes 부분을 리스너를 통해 동작하도록 수정
#        - 스케쥴 repet이 false인(단발성 스케쥴) 데이터는 실행 후 삭제한다.
#   해야할거
#        - 센서값에 따른 관련동작을 사용자에게 추천
#
##############################################################################


##############################################################################
#
# 선언 및 정의 (module 로드 및 전역번수 선언)
#
##############################################################################
import time
from datetime import datetime
from datetime import timedelta
import threading
import json
import firebase_admin
import re
import os
from firebase_admin import credentials
from firebase_admin import firestore
from module.rabbitmq import rabbitmq_clinet
from module.slack import slack

debug_msg = True

slack_token = "xoxb-2362622259573-2358980968998-mSTtdyrrEoh7fNjXdYb7wYOX"
firebase_key_path = './firebase-python-sdk-key/threeamericano-firebase-adminsdk-ejh8q-d74c5b0c68.json'
firebase_project_name = 'threeamericano'
json_file_path = "./realtimedb.json"
rt_file_path = "./server_notification"
stream_url = "http://10.8.0.2:8090/stream/video.mjpeg"
stream_detecttime = 15
stream_limittime = 60
face_recognition_path = "/home/pi/Face-Recognition/realtime_facenet_git.py"
face_recognition_result = "/home/pi/Face-Recognition/face.result"

firestore_modes_db = []
firestore_schedule_db = []
latest_schedule_check = int(time.strftime("%H%M", time.localtime(time.time()))) - 1

##############################################################################
#
# AMQP 처리 함수 지정 (서버 및 기타)
#
##############################################################################
def receive_test_test(json_data):
    print("recive test producer and command!")


def receive_server_alert(json_data):
    print("receive server alert msg!")


##############################################################################
#
# AMQP 처리 함수 지정 (차량 대쉬보드 - car)
#
##############################################################################
def receive_car_start_facer(json_data):
    # 얼굴인식 시작시 카메라장치에 얼굴인식 시작신호 메세지 발행
    docs_json_data = {}
    try:
        docs_json_data['Producer'] = "server"
        docs_json_data['command'] = "facer_sign"
        docs_json_data['sign'] = "start"
        message = json.dumps(docs_json_data, ensure_ascii=False)
        mqtt_publish('webos.camera.info', message)
    except Exception as e:
        alert_error('webos.camera.error',
                    "ERROR : 얼굴인식 시작신호 메세지를 작성/발행 중 오류가 발생했습니다. *오류명: %r" % str(e))
        return False

    # 서버측에서 얼굴인식 진행 (UV4L, openCV, TensorFlow, FaceNet)
    try:
        os.system("sudo -u pi python3.7 " + face_recognition_path)
        fr_name = read_faceresultfile(face_recognition_result)
    except Exception as e:
        alert_error('webos.car.error',
                    "ERROR : 얼굴인식 진행중 문제가 발생하였습니다. *오류명 : %r" % str(e))
        return False

    # 얼굴인식 종료후 카메라장치에 얼굴인식 종료신호 메세지 발행
    docs_json_data = {}
    try:
        docs_json_data['Producer'] = "server"
        docs_json_data['command'] = "facer_sign"
        docs_json_data['sign'] = "end"
        message = json.dumps(docs_json_data, ensure_ascii=False)
        mqtt_publish('webos.camera.info', message)
    except Exception as e:
        alert_error('webos.camera.error',
                    "ERROR : 얼굴인식 종료신호 메세지를 작성/발행 중 오류가 발생했습니다. *오류명: %r" % str(e))
        return False

    # 얼굴인식 결과로 받아온 UID를 이용하여 이름값을 받아옴.
    print("=======> %r" % fr_name)
    user_name = "fail"
    try:
        if (fr_name != "none") or (fr_name != "fail"):
            # 파이어베이스에서 해당 회원(UID)의 이름을 가져옴
            users_ref = db.collection(u'user_account').document(fr_name)
            name_docs = users_ref.get()
            name_docs_dict = name_docs.to_dict()
            user_name = name_docs_dict['name']
        else:
            print("ABCDEK")
    except Exception as e:
        print("얼굴인식 실패 예외처리: %r" % str(e))

    # 얼굴인식 결과값을 다시 자동차에게 반환
    docs_json_data = {}
    try:
        docs_json_data['Producer'] = "server"
        docs_json_data['command'] = "return_facer"
        docs_json_data['result'] = fr_name  # 해당 값이 Exception / Error / None / fail 인 경우 예외임.
        docs_json_data['name'] = user_name  # 해당 값이 fail인 경우 user_account에 이름이 없는 경우임.
        message = json.dumps(docs_json_data, ensure_ascii=False)
        print("frname %r" % str(message))
    except Exception as e:
        alert_error('webos.car.error',
                    "ERROR : 얼굴인식 결과 메세지를 보내는 도중 오류가 발생했습니다. *오류명: %r" % str(e))
        return False

    mqtt_publish('webos.car.info', message)


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


##############################################################################
#
# AMQP 처리 함수 지정 (스마트폰 - android)
#
##############################################################################
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
# 일반함수 선언 및 정의 (일반함수)
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
        mqtt_publish(routing_key, message)
    except Exception as e:
        print("========== MQTT로 에러메세지 전송에 실패했습니다.  ========== %r" % e)
        return False


def write_file(file_path, write_inform):
    rt_file = open(file_path, "wt")
    rt_file.write(str(write_inform))
    rt_file.close()
    time.sleep(0.1)


def read_jsonfile(file_path):
    with open(file_path, "rt", encoding='CP949', errors='ignore') as json_file:
        dict_data = json.load(json_file)
        return dict_data


def read_faceresultfile(file_path):
    before_time = time.time()
    while True:
        now_time = time.time()
        with open(file_path, 'r') as f:
            lines = f.readlines()
            f_name = str(lines[0].strip())
            f_time = float(lines[1].strip())
            '''
            time_interval = int(now_time - f_time)
            if time_interval < 120:  # 2분 이내에 얼굴인식 된 결과일 경우
                return f_name
            elif int(now_time - before_time) > 120:  # 얼굴인식 요청이후 2분이 경과한 경우
                return "error"
            '''
            return f_name


def json_key_is_there(json_data, key_list):
    try:
        for key in key_list:
            temp = json_data[key]
    except Exception as e:
        raise(e)


##############################################################################
#
# 일반함수 선언 및 정의 (파이어베이스)
#
##############################################################################
def dict_realtimedb_decode_smarthome(dict_data):
    # RealTimeDB를 통해 확인한 스마트홈의 가전들의 현재상태를, 각각의 변수로 변환해주는 함수 / Return : Dict
    return_dict = {}
    smarthome = dict_data['smarthome']
    status = smarthome['status']

    return_dict['mode'] = status[0:1]
    return_dict['airconEnable'] = status[1:2]
    return_dict['airconWindPower'] = status[2:3]
    return_dict['lightEnable'] = status[3:4]
    return_dict['lightBrightness'] = status[4:5]
    return_dict['lightColor'] = status[5:6]
    return_dict['lightMode'] = status[6:7]
    return_dict['windowOpen'] = status[7:8]
    return_dict['gasValveEnable'] = status[8:9]

    return return_dict


def client_notification_msg(dict_data):
    # RealTimeDB를 통해 확인한 스마트홈의 가전들의 현재상태를, 각각의 변수로 변환해주는 함수 / Return : Dict
    notification_msg = ""
    sensor = dict_data['sensor']
    hometemp = sensor['hometemp']
    openweather = sensor['openweather']
    smarthome = dict_data['smarthome']
    status = smarthome['status']
    smarthome_dict = {}

    smarthome_dict['mode'] = status[0:1]
    smarthome_dict['airconEnable'] = status[1:2]
    smarthome_dict['airconWindPower'] = status[2:3]
    smarthome_dict['lightEnable'] = status[3:4]
    smarthome_dict['lightBrightness'] = status[4:5]
    smarthome_dict['lightColor'] = status[5:6]
    smarthome_dict['lightMode'] = status[6:7]
    smarthome_dict['windowOpen'] = status[7:8]
    smarthome_dict['gasValveEnable'] = status[8:9]

    if int(smarthome_dict['gasValveEnable']) == 1:
        notification_msg = "가스벨브가 열려있어요."
    elif int(hometemp['rain']) == 1 and int(smarthome_dict['windowOpen']) == 1:
        notification_msg = "비가오니 창문을 닫아주세요."
    elif (
            (str(openweather['icon']) == "09d") or
            (str(openweather['icon']) == "09n") or
            (str(openweather['icon']) == "10d") or
            (str(openweather['icon']) == "10n") or
            (str(openweather['icon']) == "11d") or
            (str(openweather['icon']) == "11n")
         ) and int(smarthome_dict['windowOpen']) == 1:
        notification_msg = "비 소식이 있으니 창문을 닫아주세요."
    elif (
            (str(openweather['icon']) == "13d") or
            (str(openweather['icon']) == "13n")
         ) and int(smarthome_dict['windowOpen']) == 1:
        notification_msg = "눈 소식이 있으니 창문을 닫아주세요."
    elif int(openweather['air_level']) >= 2 and int(smarthome_dict['windowOpen']) == 1:
        notification_msg = "대기질이 나쁘니 창문을 닫아주세요."
    else:
        notification_msg = "none"

    return notification_msg


def dict_firestore_decode_smarthome(dict_data):
    # 스케쥴 DB 또는 MODES DB에서 가져온 dict 데이터를, 스마트홈 가전제어 프로토콜에 사용하기 위한 변수로 변환해주는 함수 / Return : Dict
    return_dict = {}
    if str(type(dict_data)) != "<class 'dict'>":
        raise Exception("인자값이 딕셔너리 클래스가 아닙니다.")

    # 모드 정보 불러오기 ()
    try:
        return_dict['mode'] = dict_data['modeNum']
    except Exception as e:
        return_dict['mode'] = '0'

    return_dict['airconEnable'] = dict_data['airconEnable']
    return_dict['airconWindPower'] = dict_data['airconWindPower']
    return_dict['lightEnable'] = dict_data['lightEnable']
    return_dict['lightBrightness'] = dict_data['lightBrightness']
    return_dict['lightColor'] = dict_data['lightColor']
    return_dict['lightMode'] = dict_data['lightMode']
    return_dict['windowOpen'] = dict_data['windowOpen']
    return_dict['gasValveEnable'] = dict_data['gasValveEnable']

    return return_dict


def dict_compare_smarthome_alarm(dict_data_ori, dict_data_now):
    global firestore_modes_db

    msg_list = []
    tm = time.localtime(time.time())
    now_time = str(tm.tm_year) + "." + str(tm.tm_mon) + "." + str(tm.tm_mday) + "." + str(tm.tm_hour) + "." + str(tm.tm_min) + "." + str(tm.tm_sec)
    # 모드 비교
    if dict_data_ori['mode'] != dict_data_now['mode'] and str(dict_data_now['mode']) != '0':
        # modes_db_copy 딕셔너리에서 이름 가져오기
        now_mode_num = str(dict_data_now['mode'])
        now_mode_name = "모드정보없음"
        for mode_data in firestore_modes_db:
            if str(mode_data['modeNum']) == str(dict_data_now['mode']):
                now_mode_name = str(mode_data['modeName'])
                break

        # 업로드할 메세지 작성
        msg_inform = now_mode_name + "가 실행되었습니다."

        # 알람 메세지 작성
        msg_list.append({
            "icon": now_mode_num + "mode_icon",
            "date": str(now_time),
            "inform": msg_inform
        })
    else:
        # 각 가전 상태비교
        msg_inform = "empty"
        if dict_data_ori['airconEnable'] != dict_data_now['airconEnable'] and  dict_data_now['airconEnable'] != '2':
            if dict_data_now['airconEnable'] == '1':
                msg_inform = "에어컨이 켜졌어요."
            else:
                msg_inform = "에어컨이 꺼졌어요."
            msg_list.append({
                "icon": "aircon_icon",
                "date": str(now_time),
                "inform": msg_inform
            })
        if dict_data_ori['lightEnable'] != dict_data_now['lightEnable'] and  dict_data_now['lightEnable'] != '2':
            if dict_data_now['lightEnable'] == '1':
                msg_inform = "전등이 켜졌어요."
            else:
                msg_inform = "전등이 꺼졌어요."
            msg_list.append({
                "icon": "light_icon",
                "date": str(now_time),
                "inform": msg_inform
            })
        if dict_data_ori['windowOpen'] != dict_data_now['windowOpen'] and  dict_data_now['windowOpen'] != '2':
            if dict_data_now['windowOpen'] == '1':
                msg_inform = "창문이 열렸어요."
            else:
                msg_inform = "창문이 닫혔어요."
            msg_list.append({
                "icon": "window_icon",
                "date": str(now_time),
                "inform": msg_inform
            })
        if dict_data_ori['gasValveEnable'] != dict_data_now['gasValveEnable'] and  dict_data_now['gasValveEnable'] != '2':
            if dict_data_now['gasValveEnable'] == '1':
                msg_inform = "가스밸브가 열렸어요."
            else:
                msg_inform = "가스밸브가 닫혔어요."
            msg_list.append({
                "icon": "gasvalve_icon",
                "date": str(now_time),
                "inform": msg_inform
            })

    # 해당을 데이터로 만듬
    print("*알람 등록할 데이터 : {}" . format(msg_list))
    return msg_list


def encode_smarthome_protocol(dict_data):
    # 딕셔너리 변수 생성
    return_dict = {}

    # 각 항목 변환
    return_dict['mode'] = str(dict_data['mode'])  # 모드값

    if dict_data['airconEnable']:
        return_dict['airconEnable'] = '1'
    else:
        return_dict['airconEnable'] = '0'
    return_dict['airconWindPower'] = str(dict_data['airconWindPower'])

    if dict_data['lightEnable']:
        return_dict['lightEnable'] = '1'
    else:
        return_dict['lightEnable'] = '0'
    return_dict['lightBrightness'] = str(dict_data['lightBrightness'])
    return_dict['lightColor'] = str(dict_data['lightColor'])
    return_dict['lightMode'] = str(dict_data['lightMode'])

    if dict_data['windowOpen']:
        return_dict['windowOpen'] = '1'
    else:
        return_dict['windowOpen'] = '0'
    if dict_data['gasValveEnable']:
        return_dict['gasValveEnable'] = '1'
    else:
        return_dict['gasValveEnable'] = '0'

    # smarthome형식의 string으로 반환
    temp_string = return_dict['mode'] + return_dict['airconEnable'] + return_dict['airconWindPower'] + \
                  return_dict['lightEnable'] + return_dict['lightBrightness'] + return_dict['lightColor'] + return_dict['lightMode'] + \
                  return_dict['windowOpen']+return_dict['gasValveEnable']

    return temp_string


def send_control_smarthome(smarthome_protocol_string):
    # 프로토콜이 맞는지 확인 (9자리)
    if len(smarthome_protocol_string) != 9:
        alert_error('data.error.error',
                    "WARNING : server측에서 스마트홈 프로토콜에 맞지않는 값을 전송하려하여, 이를 무시합니다. *함수명 : send_control_smarthome() / Value : %r" % smarthome_protocol_string)
        return False

    # MQTT를 통해 '스마트홈 가전제어' 메세지 전송
    mqtt_publish('webos.smarthome.info', smarthome_protocol_string)


def read_firestore(collection_name):
    # Firesotre Update 되었을때만 가져오는 함수가 있는지 확인
    schedule_ref = db.collection(collection_name)
    docs = schedule_ref.stream()
    '''
    for doc in docs:
        print(u'{} => {}'.format(doc.id, doc.to_dict()))
    '''
    return docs


def insert_alarm(alarm_dict):
    # 파이어스토어 업로드하기 전, 데이터 무결성 검사
    try:
        check_alarm_right(alarm_dict)
    except Exception as e:
        alert_error('data.error.error',
                    "WARNING : 잘못된 형식의 알람값을 전송하려고 합니다. 이를 무시합니다. *내용 : {0}, *오류명 : {1}".format(str(alarm_dict), str(e)))
        return False
    # 알람 발행시간 설정 (100억 - 현재시간값)
    alarm_date = int(10000000000) - int(time.time())

    # 파이어베이스에 데이터 업로드
    doc_ref = db.collection(u'appliance_alarm').document( str(alarm_date) )
    doc_ref.set(alarm_dict)


def check_alarm_right(dict_data):
    temp = dict_data['icon']
    temp = dict_data['date']
    temp = dict_data['inform']


def delete_alarm(document_name):
    #파이어베이스에 해당 문서 삭제
    db.collection(u'appliance_alarm').document(document_name).delete()


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

    # 필수 값이 있는지 확인
    temp = (dict_data['title'])
    temp = (dict_data['modeNum'])
    temp = (dict_data['enabled'])
    temp = (dict_data['startTime'])

    # 단발성 / 반복성에 따른 데이터가 있는지 확인
    if dict_data['repeat'] == False:
        temp = (dict_data['activeDate'])
    elif dict_data['repeat'] == True:
        temp = (dict_data['daysOfWeek'])
    else:
        raise Exception("해당 문서에 'repeat'값에 형식이 잘못되었습니다. 실행함수:check_schedule_right. ")

    # 해당모드에 관련 데이터가 있는지 확인
    '''
    if dict_data['modeNum']:
        pass
    else:
        pass
    '''


def check_schedule_now(dict_data):
    global latest_schedule_check

    check_state = False
    now_time = int(time.strftime("%H%M", time.localtime(time.time())))
    now_date = int(time.strftime("%Y%m%d", time.localtime(time.time())))
    start_time = int(dict_data['startTime'])

    # 최근 스케줄 동작시점과 비교하여, 현재시간이 그 시점보다 클경우에만 스케쥴 확인 진행
    if latest_schedule_check >= now_time:
        return False

    # 공통 조건 확인
    if not dict_data['enabled']:
        return False

    if (start_time) <= now_time <= (start_time + 1):
        check_state = True
    else:
        return False

    # 단발성/반복성에 따른 스케쥴 상세체크
    if dict_data['repeat'] == False:
        # 일회성 로직인 경우
        active_date = int(re.sub(r'[^0-9]', '', str(dict_data['activeDate'])[0:10]))
        print("{0} vs {1}".format(active_date, now_date))

        if active_date == now_date:
            check_state = True
        else:
            return False

    elif dict_data['repeat'] == True:
        # 주기적 로직인 경우
        now_dayoftheweek = dict_data['daysOfWeek'][int(time.strftime("%w", time.localtime(time.time())))]  # 동작 요일 확인
        if not now_dayoftheweek:
            return False
    else:
        raise Exception("해당 문서에 'repeat'값에 형식이 잘못되었습니다. 실행함수:check_schedule_now. ")

    return check_state


def on_snapshot_modes(doc_snapshot, changes, read_time):
    # 모드 데이터가 변경되면 해당 정보를 로드하고 firestore_modes_db 정보를 갱신함
    global firestore_modes_db
    modes_query = read_firestore('modes')

    # 파이어베이스에서 모드 정보 가져오기
    firestore_modes_db = []
    for mode_doc in modes_query:
        this_mode_doc = mode_doc.to_dict()
        try:
            temp = this_mode_doc['modeNum']
            temp = this_mode_doc['modeName']
        except Exception as e:
            alert_error('data.error.warning',
                        "WARNING : modes 데이터베이스에 name 또는 num이 없는 문서가 있습니다. *오류명 : %r" % str(e))
        try:
            firestore_modes_db.append(this_mode_doc)
        except Exception as e:
            alert_error('data.error.error',
                        "ERROR : modes 데이터베이스의 값을 갱신받는 도중 에러가 발생하였습니다. *오류명 : %r" % str(e))

    print("[info] modes Firestroe 정보가 수정되었습니다. ")


def on_snapshot_alarm(doc_snapshot, changes, read_time):
    # 알람 데이터가 상한선(20개)를 넘는지 확인하고 처리함
    alarm_list_limit = 20
    alarm_query = read_firestore('appliance_alarm')
    count = 1

    for alarm_doc in alarm_query:
        if count > alarm_list_limit:
            delete_alarm(alarm_doc.id)
            print("[info] 오래된 alarm 데이터를 삭제했습니다. ")
        count = count + 1


def on_snapshot_schedule(doc_snapshot, changes, read_time):
    # 스케쥴 데이터가 변경되면 해당 정보를 로드하고 firestore_schedule_db 정보를 갱신함
    global firestore_schedule_db
    schedule_query = read_firestore('schedule_mode')

    # 파이어베이스에서 모드 정보 가져오기
    firestore_schedule_db = []
    for schedule_doc in schedule_query:
        this_schedule_doc = schedule_doc.to_dict()
        this_schedule_doc['title'] = str(schedule_doc.id)
        try:
            firestore_schedule_db.append(this_schedule_doc)
        except Exception as e:
            alert_error('data.error.error',
                        "ERROR : schedule 데이터베이스의 값을 갱신받는 도중 에러가 발생하였습니다. *오류명 : %r" % str(e))

    print("[info] schedule Firestroe 정보가 수정되었습니다. ")


##############################################################################
#
# 일반함수 선언 및 정의 (AMQP - RabbitMQ)
#
##############################################################################
def on_mqtt_message(channel, method_frame, header_frame, body):
    print("[R] ecive MQTT Message")

    # 상수(int)형 메세지인지 확인 (안받아요~)
    if str(type(body)) == 'int':
        alert_error('data.error.warning',
                    "WARNING : 상수형 데이터가 들어왔습니다. 이를 무시합니다. *값 : " + str(body))

    # 메세지 내용을 JSON 형태로 정제
    try:
        body_decode = body.decode()
        json_data = json.loads(body_decode)
        # iterator = iter(json_data)
        print_debug("AMQP MSG : %r" % str(body_decode))
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
    body_decode = ""
    try:
        body_decode = body.decode()
    except Exception as e:
        print("*SmartHome on_mqtt error")

    # 데이터 형식 확인 (9글자)
    if len(body_decode) != 9:
        print("*SmartHome Protocol : Wrong Protocol is Received")
        return False

    '''
    # 사용할 데이터 정제
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
    '''

    # 현재 상태를 확인하여 어떤 정보를 업데이트해야되는지 확인 (보낼것들을 List로 작성)
    print("*SmartHome Protocol : {0}".format(body_decode))

    # 더 이상 RealTimeDB에 모드값을 서버가 업데이트하지 않음.
    # write_mode_state(mode_file_path, mode)


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

# FireStore Listener 생성
modes_watch = db.collection('modes').on_snapshot(on_snapshot_modes)
alarm_watch = db.collection('appliance_alarm').on_snapshot(on_snapshot_alarm)
schedule_watch = db.collection('schedule_mode').on_snapshot(on_snapshot_schedule)

# RealTime DB 값 불러오기
print_debug("[init] Load RealTime DB JSON")
smarthome_appliance_now = {}
smarthome_appliance_before = {}
try:
    rtdb_dict_data = read_jsonfile(json_file_path)  # 정안되면 이걸 json이 아닌 config로 만들어..?
    smarthome_appliance_now = dict_realtimedb_decode_smarthome(rtdb_dict_data)
    smarthome_appliance_before = smarthome_appliance_now
except Exception as e:
    alert_error("data.error.error",
                "ERROR : RealTimeDB.JSON을 불러오는 중에 오류가 발생하였습니다. 확인이 필요합니다. *오류명 : %r" % str(e))

# RabbitMQ 구독 진행 (쓰레드 실행)
print("[init] RabbitMQ Thread (webos.server)")
t = threading.Thread(target=thread_consume_queue, daemon=True)  # webos.server
t.start()
time.sleep(4)

print("[init] RabbitMQ Thread (data.smarthome)")
t2 = threading.Thread(target=thread_consume_smarthome, daemon=True)  # data.smarthome
t2.start()
time.sleep(4)

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
        rtdb_dict_data = read_jsonfile(json_file_path)  # CP949 형식으로 수정. (문제발생시 configPasere(ini) 형식으로 수정)
        smarthome_appliance_now = dict_realtimedb_decode_smarthome(rtdb_dict_data)
    except Exception as e:
        alert_error("data.error.error",
                    "ERROR : RealTimeDB.JSON을 불러오는 중에 오류가 발생하였습니다. 확인이 필요합니다. *오류명 : %r" % str(e))

    # 가전현상태의 이전값과 현재값을 비교하여 차이가 있는 경우 이를 알람(Firestore)으로 발생시킴
    print_debug("[A] check smarthome appliance status is changed")
    try:
        print_debug(" ┗[1] 스마트홈 가전상태 변화 확인")
        # print_debug("   ┗[2] 가전 이전상태 : %r" % str(smarthome_appliance_before.values()))
        # print_debug("   ┗[2] 가전 현재상태 : %r" % str(smarthome_appliance_now.values()))

        if smarthome_appliance_now != smarthome_appliance_before:
            print_debug(" ┗[2] 가전제어값에 변화 있음")
            msg_list = dict_compare_smarthome_alarm(smarthome_appliance_before, smarthome_appliance_now)

            print_debug(" ┗[3] 알람메시지 작성완료")
            # 파이어스토어에 알람 데이터 추가
            for alarm_msg in msg_list:
                print_debug("  ┗[1] 알람메시지 파이어스토어에 발행")
                insert_alarm(alarm_msg)

            # 알람 데이터 갯수가 많을 경우 이전내용부터 순차적으로 제거
            # alarm firestore listner callback 함수가 이를 처리

            # 동작완료 후, 이전 스마트홈 값을 최신값으로 갱신
            print_debug(" ┗[4] 가전제어 저장값 갱신")
            smarthome_appliance_before = smarthome_appliance_now
    except Exception as e:
        alert_error('data.error.error',
                    "WARNING : 스마트홈 가전 변동사항 감지 중 오류가 발생하였습니다. 확인이 필요합니다. *오류명 : %r" % str(e))

    # 사용자에게 알려야하는 사항이 있는지 확인한후, 해당 내용을 realtimeDB에 기록하기 위해 파일에 저장
    notification_msg = client_notification_msg(rtdb_dict_data)
    if notification_msg != "":
        write_file(rt_file_path, notification_msg)

    # 현재시점에서 처리해야하는 Schedule이 있는지 확인
    print_debug("[A] Load FireStore Schedule")
    #try:
    # 각 문서(doc)별로 내용 분석
    update_latest_schedule_run_time = False
    for doc in firestore_schedule_db:
        schedule_dict = doc
        #schedule_dict['mode'] = '0'
        try:
            # DB에 저장되어있던 스케쥴 형식이 정상적인 형식인지 확인
            check_schedule_right(schedule_dict)
        except Exception as e:
            alert_error("data.error.error",
                        "WARNING : FireStore DB에 형식이 잘못된 데이터가 있습니다. 확인이 필요합니다. *문서ID : " +
                        str(schedule_dict['title']) + " / *오류명 : " + str(e))
            continue

        # 현재 실행해야 하는 스케쥴인지 확인
        if check_schedule_now(schedule_dict):
            print_debug(" ┗[1] Time to execute this schedule. *Name : %r" % str(schedule_dict['title']))

            # 모드(modeNum)값을 확인하여 0이 아니면, 모드로 판단하여 modes에 값을 불러옴
            if str(schedule_dict['modeNum']) == '0':
                # 스케쥴 데이터를 '스마트홈 프로토콜 형식'으로 생성
                schedule_appliance = dict_firestore_decode_smarthome(schedule_dict)
            else:
                # 모드값이 있는 경우 해당 모드에 정보를 불러와 '스마트홈 프로토콜 형식'으로 생성
                for mode_doc in firestore_modes_db:
                    if mode_doc['modeNum'] == schedule_dict['modeNum']:
                        schedule_appliance = dict_firestore_decode_smarthome(mode_doc)
                        break

            # 스케쥴값과 실시간DB값을 비교하여, 실행해야 하는 명령만 명령으로 확정
            flag_sendmsg = False
            if schedule_appliance['airconEnable'] != smarthome_appliance_now['airconEnable'] and \
                    schedule_appliance['airconEnable'] != '2':  # On/Off가 기존과 상이하고, 현행유지 상태가 아닌경우
                flag_sendmsg = True
            elif schedule_appliance['airconEnable'] == True and \
                    schedule_appliance['airconWindPower'] != smarthome_appliance_now['airconWindPower']:  # 풍량 값이 다른 경우
                flag_sendmsg = True

            if schedule_appliance['lightEnable'] != smarthome_appliance_now['lightEnable'] and \
                    schedule_appliance['lightEnable'] != '2':  # On/Off가 기존과 상이하고, 현행유지 상태가 아닌경우
                flag_sendmsg = True
            elif schedule_appliance['lightEnable'] == True and (
                    schedule_appliance['lightBrightness'] != smarthome_appliance_now['lightBrightness'] or
                    schedule_appliance['lightColor'] != smarthome_appliance_now['lightColor'] or
                    schedule_appliance['lightMode'] != smarthome_appliance_now['lightMode']):  # 전등 상세값이 다른 경우
                flag_sendmsg = True

            if schedule_appliance['windowOpen'] != smarthome_appliance_now['windowOpen'] and \
                    schedule_appliance['windowOpen'] != '2':  # On/Off가 기존과 상이하고, 현행유지 상태가 아닌경우
                flag_sendmsg = True
            if schedule_appliance['gasValveEnable'] != smarthome_appliance_now['gasValveEnable'] and \
                    schedule_appliance['gasValveEnable'] != '2':  # On/Off가 기존과 상이하고, 현행유지 상태가 아닌경우
                flag_sendmsg = True

            # 새로 진행해야할 명령이 있따면, 해당명령을 '스마트홈 큐'로 전달
            if flag_sendmsg:
                print(" ┗[2] send control msg to smarthome")
                send_control_smarthome(encode_smarthome_protocol(schedule_appliance))
                update_latest_schedule_run_time = True
            # 명령 전달이후 once 인 메세지는 스케쥴에서 삭제진행
            if schedule_dict['repeat'] == False:
                print(" ┗[3] delete schedule (cuz it is 'repeat: False')")
                delete_schedule(schedule_dict['title'])

    # 스케쥴 관련 동작을 실행한경우 '최종스케줄 실행시간(lateset_schedule_check)' 갱신
    now_time_hhmm = int(time.strftime("%H%M", time.localtime(time.time())))
    if update_latest_schedule_run_time:
        latest_schedule_check = now_time_hhmm
    elif (now_time_hhmm <= 1):
        latest_schedule_check = -1
    '''
    except Exception as e:
        alert_error("data.error.error",
                    "ERROR : FireStore Schedule 값을 처리하는 중 오류가 발생하였습니다. 확인이 필요합니다. *오류명 : %r" % str(e))
    '''
    # 또 어떤 로직이 이곳에 오게될것인가~

    # 동작대기
    time.sleep(1)

