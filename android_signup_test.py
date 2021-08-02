#-*-coding:utf-8-*-
#위 구문은 한글처리를 위해 필수임.
import json
import pika
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = pika.PlainCredentials('rabbit','MQ321') #MQTT계정 ID,PW를 차례로 입력
connection = pika.BlockingConnection(pika.ConnectionParameters(host='211.179.42.130',port=5672,credentials=cred)) #MQTT서버의 IP, Port를 입력
channel = connection.channel()

# 사용할 exchange 이름과 type(direct, topic, fanout ..)을 입력합니다.
channel.exchange_declare(exchange='webos.topic', exchange_type='topic')



def callback(ch, method, properties, body):	
	print("\n\n[MQTT Reciving Message]")
	print(" [x] Received %r" % body.decode())

	# 받아온 JSON 데이터를 파싱
	print("\n\n[JSON DATA]")
	data = body.decode()
	json_data = json.loads(data)
	print(json_data)
	
	print("\n\n[SignUp Data from Arduino App.]")

	# 파이어베이스에 접속하여 관련 데이터 추가하기
	if json_data['command'] == "signup" :	
		print(" - Producer : %r" % json_data['Producer'])
		print(" - command : %r" % json_data['command'])
		print(" - UID : %r" % json_data['UID'])
		print(" - name : %r" % json_data['name'])
		print("==========[Firestore Write]==========")
		doc_ref = db.collection(u'user_account').document(json_data['UID'])
		doc_ref.set({
			u'name': json_data['name']
		})
		print("==========[Okay]==========")
		
	elif json_data['command'] == "signin" :
		print(" - Producer : %r" % json_data['Producer'])
		print(" - command : %r" % json_data['command'])
		print(" - UID : %r" % json_data['UID'])
		print("==========[Firestore Read]==========")
		
		#Firestore에서 UID 기준으로 문서 읽기
		print("==========[Read]==========")
		users_ref = db.collection(u'user_account').document(json_data['UID'])
		docs = users_ref.get()

		#docs_json_data에 데이터 반환.
		if docs.exists:
			#print(f'Document data: {docs.to_dict()}')
			docs_json_data = docs.to_dict()
			docs_json_data['Producer']="server"
			docs_json_data['command']="return_name"
			docs_json_dump = json.dumps(docs_json_data)
			print(docs_json_dump)
		else:
			print(u'No such document!')
			
		#MQTT를 통해 '이름값 반환' 메세지 전송
		message = docs_json_dump
		channel.basic_publish(exchange='webos.topic', routing_key='webos.android.info', body=message)
		print("\n [x] Sent %r" % message)

	else :
		print("\n\nis not signup/signin command, this is the signup function test program\n\n")


# 파이어베이스 프로젝트에 접속하기
print("==========[Firebase Init]==========")
cred = credentials.Certificate('./firebase-python-sdk-key/threeamericano-firebase-adminsdk-ejh8q-d74c5b0c68.json')
firebase_admin.initialize_app(cred, {
	'projectID': 'threeamericano',
})
db = firestore.client()	



# MQTT Queue Consumer(구독) 하기
channel.basic_consume(queue='webos.server', on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
