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




__open_channel__ ()

​	RabbitMQ 서버에 통신을 위한 채널을 생성합니다. `connect_server`를 먼저 실행해야합니다.

- return : `channel`




__publish_queue__ (queue_name, message)

​	특정 Queue에 직접 메세지를 발행합니다.

- queue_name : 메세지를 발행할 큐를 선택합니다.
- message : 실제 전송할 메세지 입니다.

- return : `null`






__publish_exchange__ (ec, rk, message)

​	Routing Key를 이용하여 exchange에 메세지를 발행합니다.

- ec : 메세지를 발행할 Exchange를 선택합니다.
- rk : 분류를 위한 Routing_key를 명시하여, 메세지와 함께 보냅니다.
- message : 실제 전송할 메세지 입니다.

- return : `null`






__consume_setting__ (queue_name, cb_function)

​	메세지를 왔는지 확인할 큐 이름과, 메세지가 왔을 때 실행할 함수를 명시합니다. 이때 ack는 True로 설정되어있습니다.

- queue_name : 메세지를 구독할 큐를 선택합니다.
- cb_function : 메세지가 도착했을 때 실행할 callback 함수를 명시합니다.

- return : `null`






__consume_starting__ ()

​	`consume_setting` 에 명시한 정보를 기반으로 메세지 구독을 시작합니다.

- return : `null`




__consume_stop__ ()

​	현재 진행하고있는 구독을 중지합니다.

- return : `null`






__consume_auto__ (queue_name)

​	메세지를 구독할 큐 이름을 입력하면, 바로 구독을 시작하며 도착한 메세지를 실시간으로 콘솔에 출력합니다.

- return : `null`







__consume_nacktest__ (queue_name)

​	메세지를 구독할 큐 일므을 입력하면, 바로 구독을 시작합니다. 이 때 메세지는 `ack = false` 처리되어 소비되지 않습니다.

- return : `null`














