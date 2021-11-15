import pika
import weather_api as wa

# #####################################
# Rabbit MQ Server 연결
# #####################################
cred = pika.PlainCredentials('rabbit','MQ321') #MQTT계정 ID,PW를 차례로 입력
connection = pika.BlockingConnection(pika.ConnectionParameters(host='<<SERVER IP>>',port=5672,credentials=cred)) #MQTT서버의 IP, Port를 입력
channel = connection.channel()


# #####################################
# 동작
# #####################################
weather_data = wa.getUltraSrtNcst("60","128") # weather API 값 가져오기

message = weather_data
channel.basic_publish(exchange='webos.topic', routing_key='data.weatherapi.info', body=message)
print(" [x] Sent %r" % message)
connection.close()
