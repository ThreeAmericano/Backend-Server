import pika

cred = pika.PlainCredentials('rabbit','MQ321') #MQTT계정 ID,PW를 차례로 입력
connection = pika.BlockingConnection(pika.ConnectionParameters(
	host='<<SERVER IP>>',
	port=5672,
	credentials=cred
)) #MQTT서버의 IP, Port를 입력
channel = connection.channel()

#channel.queue_declare(queue='icecoffe') #사용할 queue를 정의 (해당 queue가 없다면 새로 생성)

def callback(ch, method, properties, body):
	print(" [x] Received %r" % body.decode())

channel.basic_consume(queue='data.weatherapi', on_message_callback=callback, auto_ack=False)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
