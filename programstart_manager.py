#-*-coding:utf-8-*-
##############################################################################
#
#       [ Server Start Management Program ]
#   작성일 : 2021-08-13
#   작성자 : 최현식(chgy2131@naver.com)
#   변경점
#        - 최초작성
#
##############################################################################
import os
from module.slack import slack

def alert_error(message):
	print(message)
	sl.slack_post_message('#server', message)

# Slack Bot 개체 생성하기
sl = slack.SlackBot(token="xoxb-2362622259573-2358980968998-mSTtdyrrEoh7fNjXdYb7wYOX")
alert_error("INFORM : 서버 매니지먼트 프로그램 및 처리프로그램이 시작되었습니다.")

while True :
	try:
		# 메인 프로그램 가동
		os.system('python3 ./backend_process.py')
	except Exception as e:
		# 문제발생시 오류메세지 송출
		alert_error("ERROR : 서버 프로그램이 예상치 못한 상황으로 인해 종료되었습니다. *오류명 : %r" % str(e))
	alert_error("INFORM : 서버 처리프로그램이 재가동됩니다.")
