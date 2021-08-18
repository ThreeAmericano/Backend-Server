# -*-coding:utf-8-*-
##############################################################################
#
#       [ 파이어베이스 스케줄 조회 로직 샘플 Program ]
#   수정일 : 2021-08-18
#   작성자 : 최현식(chgy2131@naver.com)
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
import datetime  # <- 추가해야됨
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import re

slack_token = "xoxb-2362622259573-2358980968998-mSTtdyrrEoh7fNjXdYb7wYOX"
firebase_key_path = '../firebase-python-sdk-key/threeamericano-firebase-adminsdk-ejh8q-d74c5b0c68.json'
firebase_project_name = 'threeamericano'
json_file_path = "./realtimedb.json"


##############################################################################
#
# 선언 및 정의 (일반함수)
#
##############################################################################

def alert_error(routing_key, message):
    print(message)


def read_jsonfile(file_path):
    with open(file_path, "r") as json_file:
        dict_data = str(json.load(json_file))
        return dict_data


def json_key_is_there(json_data, key_list):
    for key in key_list:
        temp = json_data[key]


###############################################################################

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


##############################################################################
#
# 초기설정 (Init)
#
##############################################################################
# 파이어베이스 프로젝트에 접속하기
cred = credentials.Certificate(firebase_key_path)
firebase_admin.initialize_app(cred, {
    'projectID': firebase_project_name,
})
db = firestore.client()

##############################################################################
#
# 반복 실행
#
##############################################################################
#while True:
'''
# 일회성 업데이트 예제
update_schedule('schedule_mode', '돈벌시간', {
    'Enabled': True,
    'One_time': True,
    'UID': 'DONVERSIGAN123',
    'Active_date': datetime.datetime.now(),
    'Device_ex': "EXAMPLE"
    # DEVICE 제어 내용
})

# 지속성 업데이트 예제
update_schedule('schedule_mode', '돈벌시간2', {
    'Enabled': True,
    'One_time': False,
    'UID': 'DONVERSIGAN123',
    'Daysofweek': [True, True, True, True, True, True, True],
    'Start_time': "2000",
    'End_time': "0230",
    'Device_ex': "EXAMPLE"
    # DEVICE 제어 내용
})
'''
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
                        "WARNING : FireStore DB에 형식이 잘못된 데이터가 있습니다. 확인이 필요합니다. *문서ID : " + str(
                            doc.id) + " / *오류명 : " + str(e))
            continue

        # 현재 실행해야 하는 스케쥴인지 확인
        print(check_schedule_now(schedule_dict))
        if check_schedule_now(schedule_dict):
            pass

except Exception as e:
    alert_error("data.error.error",
                "ERROR : FireStore Schedule 값을 처리하는 중 오류가 발생하였습니다. 확인이 필요합니다. *오류명 : %r" % str(e))

'''
for key in schedule_dict:
    print(key)
    print(schedule_dict[key])
'''