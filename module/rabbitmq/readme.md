# rabbitmq_client 모듈

20201-08-10, 작성자 : 최현식



### 용도

Rabbit MQTT 서버에 접속하여 메세지를 발행/수신 하기 위한 모듈입니다. 기존 `pika` 모듈에 의존성이 있습니다.



### 예시

```python
# 서버의 정보를 입력한뒤에 접속합니다.
rb = RabbitmqClient('211.179.42.130', 5672, 'rabbit', 'MQ321')
rb.connect_server()

# 통신채널을 열어 실제 통신을 진행합니다. 이때 return값을 이용하여 직접 pika 함수를 사용할 수 있습니다.
direcht_control = rb.open_channel()

# 메세지를 보냅니다.
rb.publish_queue('test321', 'messageeeeeee')
```



### 함수

__init__ (ip, port, rbmq_id, rbmq_pw)

​	최초로 class를 만들때 사용됩니다.

- ip : RabbitMQ 서버의 IP를 입력합니다.
- port : RabbitMQ 서버의 PORT를 입력합니다.
- rbmq_id : RabbitMQ 서버에 접속할 계정 아이디를 입력합니다.
- rbmq_pw : RabbitMQ 서버에 접속할 계정의 비밀번호를 입력합니다.
- return : `null`



__connect_server__ ()

​	`init` 함수에서 받아온 RabbitMQ 서버 정보로 접속을 시도합니다.

- return : `null`



__disconnect_server__ ()

​	RabbitMQ 서버와의 연결을 끊습니다.

- return : `null`







