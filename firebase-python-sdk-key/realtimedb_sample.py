import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import time

key_path = 'threeamericano-firebase-adminsdk-ejh8q-d74c5b0c68.json'

cred = credentials.Certificate(key_path)
firebase_admin.initialize_app(cred,{
		'databaseURL' : 'https://threeamericano-default-rtdb.firebaseio.com/'
})

dir = db.reference()
dir.update({'car':'fuckyou'})

i = 0 
while True:
	time.sleep(1)
	i = i + 1
	dir.update({'car':str('hello'+str(i))})
	print("-")

