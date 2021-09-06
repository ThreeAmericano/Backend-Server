#-*-coding:utf-8-*-
##############################################################################
#
#       [ Server Start Management Program ]
#   작성일 : 2021-08-22
#   작성자 : 최현식(chgy2131@naver.com)
#   변경점
#        - 각 프로그램 분기를 쓰레드가 아닌 멀티프로세싱 방식으로 변경
#		 - 재시작시 MQTT등 강제로 종료된 강제 연결들을 정정하는 로직을 추가??
#
##############################################################################
import os
import time
import multiprocessing as mp
from module.slack import slack

slack_bot_token = "xoxb-2362622259573-2358980968998-mSTtdyrrEoh7fNjXdYb7wYOX"


def alert_error(message):
	print(message)
	sl.slack_post_message('#server', message)


def backend_process():
	while True :
		try:
			# 메인 프로그램 가동
			os.system('python3 ./backend_process.py')
		except Exception as e:
			# 문제발생시 오류메세지 송출
			alert_error("ERROR : 서버 프로그램(backend_process.py)이 예상치 못한 상황으로 인해 종료되었습니다. *오류명 : %r" % str(e))
		alert_error("INFORM : 서버 처리프로그램(backend_process.py)이 재가동됩니다.")


def realtimedb_connect():
	while True :
		try:
			# 메인 프로그램 가동
			os.system('python3 ./realtimedb_connect.py')
		except Exception as e:
			# 문제발생시 오류메세지 송출
			alert_error("ERROR : 서버 프로그램(realtimedb_connect)이 예상치 못한 상황으로 인해 종료되었습니다. *오류명 : %r" % str(e))
		alert_error("INFORM : 서버 처리프로그램(realtimedb_connect)이 재가동됩니다.")


# Slack Bot 개체 생성하기
sl = slack.SlackBot(token=slack_bot_token)
alert_error("INFORM : 서버 매니지먼트 프로그램 및 하위 프로세스가 시작됩니다.")

# 쓰레드 실행
mp_bp = mp.Process(target=backend_process, daemon=True)
mp_bp.start()
mp_rc = mp.Process(target=realtimedb_connect, daemon=True)
mp_rc.start()

# 대기 (추후 여기에 서버 관련 모니터링 추가)
while True:
	time.sleep(3600)
