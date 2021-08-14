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

# 파이어베이스 RealTime DB에 값 업데이트하기
rtdb = db.reference()
for key in ow_dict:
    rtdb.child("sensor").child("openweather").update({key: ow_dict[key]})
