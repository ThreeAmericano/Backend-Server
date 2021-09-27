import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import time
import datetime
 
#Firebase database(Firstore) 인증 및 앱 초기화
print("==========[Init]==========")
cred = credentials.Certificate('threeamericano-firebase-adminsdk-ejh8q-d74c5b0c68.json')
firebase_admin.initialize_app(cred, {
	'projectID': 'threeamericano',
})
db = firestore.client()


#반복성 스케쥴 데이터 쓰기
print("==========[repeat schedule Write]==========")
doc_name = 'title_sample3'
doc_ref = db.collection(u'schedule_mode').document(doc_name)
doc_ref.set({
    u'title': doc_name,
    u'name': 'abcdek',
    u'repeat': True,
	u'modeNum': 0,

	u'enabled': True,
	u'daysOfWeek': [
	False,
	False,
	False,
	False,
	False,
	False,
	True
	],
	u'startTime': '0710',
	
	u'airconEnable': False,
	u'airconWindPower': 9,
	u'gasValveEnable': False,
	u'lightEnable': False,
	u'lightBrightness': 5,
	u'lightColor': 2,
	u'lightMode': 3,
	u'windowOpen': False
})




'''
#단발성 스케쥴 데이터 쓰기
print("==========[repeat schedule Write]==========")
doc_name = 'title_sample_norepeat3'
doc_ref = db.collection(u'schedule_mode').document(doc_name)
doc_ref.set({
    u'title': doc_name,
    u'name': 'EK',
    u'repeat': False,
	u'modeNum': 0,

	u'enabled': False,
	u'startTime': '1900',
	u'activeDate': '2021.09.22',
	
	u'airconEnable': True,
	u'airconWindPower': 5,
	u'gasValveEnable': True,
	u'lightEnable': True,
	u'lightBrightness': 5,
	u'lightColor': 2,
	u'lightMode': 3,
	u'windowOpen': True
})
'''







#데이터 읽기
'''
print("==========[Read]==========")
users_ref = db.collection(u'thisistest')
docs = users_ref.stream()

for doc in docs:
    print(u'{} => {}'.format(doc.id, doc.to_dict()))

i = 0
while True:
	time.sleep(5)
	i = i + 1
	doc_ref = db.collection(u'thisistest').document(u'id')
	doc_ref.set({
    	u'level': i,
    	u'money': 700,
    	u'job': "knight"
	})
'''


