import pika


def connect_server(ip, port, id, pw) :
    # RabbitMQ 계정 ID,PW를 차례로 입력
    cred = pika.PlainCredentials(id, pw)
    # MQTT 서버 접속
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=ip,
        port=port,
        credentials=cred
    ))
    return connection


def open_channel(conn) :
    channel = conn.channel()
    return channel


def disconnect_server(conn) :
    conn.close()


def publish_queue(conn, rk, bd) :
    conn.basic_publish(exchange='', routing_key=rk,body=bd)  # exchange, routing_key, body(message)를 차례로 입력


if __name__ == "__main__":
    conn = connect_server('211.179.42.130', 5672, 'rabbit', 'MQ321')
    channel = open_channel(conn)
    publish_queue(channel, 'test321', 'messageeeeeee')
    disconnect_server(conn)
    print("main")

