"""
RabbitMQ, AMQP 0-9-1 Python3 기준 작성됨
2021-08-05 /  https://github.com/chhs2131
"""
import pika
import time


def __on_message(channel, method_frame, header_frame, body):
    print(method_frame.delivery_tag)
    print(body)
    print(channel.basic_ack(delivery_tag=method_frame.delivery_tag))


class RabbitmqClient:
    conn = 'no connection'
    channel = 'no channel'

    def __init__ (self, ip, port, rbmq_id, rbmq_pw) :
        self._ip = ip
        self._port = port
        self._id = rbmq_id
        self._pw = rbmq_pw

    def connect_server(self):
        # RabbitMQ 계정 ID,PW 대입
        cred = pika.PlainCredentials(self._id, self._pw)
        # RabbitMQ 서버 접속
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=self._ip,
            port=self._port,
            credentials=cred
        ))
        self.conn = connection

    def disconnect_server(self):
        # RabbitMQ 연결 해제 : 브로커 측으로 code 0 과 , 메세지를 보냅니다.
        self.conn.close(0, 'python : Normal shutdown')

    def open_channel(self):
        # RabbitMQ 채널 연결
        self.channel = self.conn.channel()
        return self.channel

    def publish_queue(self, queue_name, message):
        # 원하는 Queue에 직접 메세지를 발행. queue_name(=routing_key)
        self.channel.basic_publish(exchange='', routing_key=queue_name,body=message)  # exchange, routing_key, body(message)를 차례로 입력

    def publish_exchange(self, ec, rk, message):
        # 원하는 exchange에 메세지를 발행.
        self.channel.basic_publish(exchange=ec, routing_key=rk, body=message)

    def consume_setting(self, queue_name, callback_function):
        # 메세지를 불러올 Queue 정보를 등록하고, 메세지가 불러와질 떄 cb_function 함수를 실행함.
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback_function, auto_ack=True)

    def consume_get(self, queue_name):
        # 해당 큐에 메세지 한개를 불러옵니다.
        method_frame, header_frame, body = self.channel.basic_get(queue=queue_name, auto_ack=True)
        return body

    def consume_starting(self):
        # 메세지 불러오기를 시작함.
        self.channel.start_consuming()

    def consume_stop(self):
        # 메세지 불러오기를 중단함.
        self.channel.stop_consuming()

    def consume_auto(self, queue_name):
        # 메세지를 불러올 Queue 정보를 입력하면 자동으로 불러오기 시작함.
        self.channel.basic_consume(queue=queue_name, on_message_callback=__on_message)
        try:
            self.consume_starting()
        except KeyboardInterrupt:
            self.consume_stop()

    def consume_nacktest(self, queue_name):
        # 메세지를 불러올 Queue 정보를 입력하면 일정 시간마다 체크함. 대신 메세지를 소비하진 않음.
        while True:
            try:
                method_frame, header_frame, body = self.channel.basic_get(queue=queue_name, auto_ack=False) # 메세지를 NACK(확인하지않음) 상태로 가져옴
                if method_frame:
                    print(method_frame, header_frame, body)
                    self.channel.basic_recover(requeue=True) #대기상태에 있는 NACK 메세지를 반려함. (즉, 다시 QUEUE에 등록됨)
                else:
                    print('No message returned')
                time.sleep(3)
            except KeyboardInterrupt:
                break


if __name__ == "__main__":
    #아래는 테스트 코드입니다.
    rb = RabbitmqClient('<<SERVER IP>>', 5672, 'rabbit', 'MQ321')
    rb.connect_server()
    hello = rb.open_channel()

    rb.publish_queue('test321', 'messageeeeeee')
    rb.publish_exchange('webos.topic', 'webos.server.info', '{hello}')

    def callback(ch, method, properties, body):
        print(method.delivery_tag)
        print(" [x] Received %r" % body.decode())

    rb.consume_nacktest('webos.server')
    #rb.consume_setting('webos.server', callback)
    #rb.consume_starting()
    rb.disconnect_server()
    print("main")

