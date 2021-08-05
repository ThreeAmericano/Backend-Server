#!/usr/bin/env python
import pika

# #####################################
#
# Rabbit MQ Server 연결
#
# #####################################
cred = pika.PlainCredentials('rabbit','MQ321') #MQTT계정 ID,PW를 차례로 입력
connection = pika.BlockingConnection(pika.ConnectionParameters(host='211.179.42.130',port=5672,credentials=cred)) #MQTT서버의 IP, Port를 입력

channel = connection.channel()


# #####################################
#
# 동작
#
# #####################################
channel.queue_declare(queue='sensor') #메세지를 사용할 큐를 선택(없다면 새로만듬)

channel.basic_publish(exchange='',  routing_key='sensor', body='message example') #exchange, routing_key, body(message)를 차례로 입력
 
connection.close()
