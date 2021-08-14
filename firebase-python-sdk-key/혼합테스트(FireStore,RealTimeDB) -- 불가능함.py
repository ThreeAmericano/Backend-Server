import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
 
#Firebase database(Firstore) 인증 및 앱 초기화
print("==========[Init]==========")
cred = credentials.Certificate('threeamericano-firebase-adminsdk-ejh8q-d74c5b0c68.json')
firebase_admin.initialize_app(cred, {
	'projectID': 'threeamericano',
})
db = firestore.client()


# realtime db
key_path = 'threeamericano-firebase-adminsdk-ejh8q-d74c5b0c68.json'

cred = credentials.Certificate(key_path)
firebase_admin.initialize_app(cred,{
		'databaseURL' : 'https://threeamericano-default-rtdb.firebaseio.com/'
})

dir = db.reference()
#dir.update({'car':'ehehe'})


#데이터 쓰기
print("==========[Write]==========")
doc_ref = db.collection(u'thisistest').document(u'id')
doc_ref.set({
    u'level': 20,
    u'money': 700,
    u'job': "knight"
})

#데이터 읽기
print("==========[Read]==========")
users_ref = db.collection(u'thisistest')
docs = users_ref.stream()

for doc in docs:
    print(u'{} => {}'.format(doc.id, doc.to_dict()))



dir.update({'car':'ehehe'})



