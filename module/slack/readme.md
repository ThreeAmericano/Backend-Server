# slack 모듈

20201-08-11, 작성자 : 최현식



### 용도

Slack에서 제공하는 Bot API 기능을 활용하여 메세지를 보내는 용도입니다. 파이썬에서 기본적으로 제공하는 `requests` 모듈에 의존성이 있습니다.



### 예시

```python
# 슬랙에서 발행한 암호토큰(xoxb)을 사용하여 개체를 생성합니다.
sl = SlackBot("xoxb-token정보")

# 슬랙으로 해당채널에 메세지를 보냅니다.
sl.slack_post_message('#server', 'test') # server채널에 test라는 메시지 전달.
```



### 사전작업

1. 슬랙에서 해당 워크스페이스용 BOT을 생성하고, Token을 발급받기
2. 메세지를 보낼 채널에 BOT 계정 추가하기



## SlackBot 함수

__init__ (token)

​	최초로 class를 만들때 사용됩니다.

- token : 슬랙BOT이 사용할 Token 정보를 입력합니다.
- return : `null`




__slack_post_message__ (channel, msg)

​	원하는 `#채널` 에 채팅을 보냅니다.

- channel : 채팅을 보낼 채널명을 입력합니다. 이때 `#` 도 포함해야합니다.
- msg : 채팅으로 전달할 내용을 입력합니다.

- return : `null`


