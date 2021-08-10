"""
Thread
일단 가장 기본적인 threading.Thread를 이용하는 방법 입니다. threading.Thread(group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None) 객체의 생성자의 파라미터는 다음과 같습니다.

target: Thread의 run() 함수를 통해 돌리고 싶은 함수를 넣는다. function을 인자로 받는다.
args: target으로 넣은 함수의 args 파라미터 값을 iterable 한 객체로 넣으면 된다.
kwargs: target으로 넣은 함수의 kwargs 파라미터 값을 dict 객체로 넣으면 된다.
name: Thread 객체의 이름을 정한다. 없으면 "Thread-N" 이라는 unique한 값으로 정해진다. (N은 숫자다.)
group: Thread를 그룹화 하여 실행할 때 사용 한다.
daemon: Thread를 Daemon Thread로 만들고 싶을 때 사용 한다.
또한, threading.Thread 객체의 내부 멤버함수 입니다.

run(): Thread에 등록 된 함수를 실행합니다.
getName(), setName(): 스레드 이름의 getter/setter 함수 입니다.
is_alive(): 스레드가 실행 중인지를 반환 합니다.
isDaemon(), setDaemon(): 데몬 스레드를 지정하는 getter/setter 함수 입니다.
"""
import threading
import time


# 사용할 함수 지정
def test(a):
    while a < 100 :
        print("Thread Output => %r" % a)
        a = a + 1
        time.sleep(1)


def noargs():
    while True :
        print("=========")
        time.sleep(2)


# 쓰레드 개체 선언 및 실행
t = threading.Thread(target=test, args=(1,), daemon=True)
t.start()

t2 = threading.Thread(target=noargs, daemon=True)
t2.start()


# 메인 쓰레드 출력
zzz = 0
while zzz < 100 :
    print(" MainThread => %r" % zzz)
    zzz = zzz + 1
    time.sleep(1)
