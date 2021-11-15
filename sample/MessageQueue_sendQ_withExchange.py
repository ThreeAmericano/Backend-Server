#!/usr/bin/env python
import pika

# #####################################
#
# Rabbit MQ Server 연결
#
# #####################################
cred = pika.PlainCredentials('rabbit','MQ321') #MQTT계정 ID,PW를 차례로 입력
connection = pika.BlockingConnection(pika.ConnectionParameters(host='<<SERVER IP>>',port=5672,credentials=cred)) #MQTT서버의 IP, Port를 입력

channel = connection.channel()


# #####################################
#
# 동작
# 사용할 exchange 이름과 type(direct, topic, fanout ..)을 입력합니다.
# #####################################
channel.exchange_declare(exchange='test321', exchange_type='direct')

message = "info: Hello World!"
channel.basic_publish(exchange='test321', routing_key='amqtest', body=message)
print(" [x] Sent %r" % message)
connection.close()
