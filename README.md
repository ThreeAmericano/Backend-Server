# Backend Server (처리서버)

본 문서에서는 백엔드 처리서버에 대해 다룹니다. (MQTT Broker 및 얼굴인식 부분은 본 문서에서 다루지 않습니다.)



### 프로젝트 구조

```c#
📂Backend-Server
	┗ 📁firebase-python-sdk-key //파이어베이스 접속을 위한 KEY를 보관
		┗ 📃<firebase-sdk-key>.json
	┗ 📁module //각 모듈라이브러리를 저장
        ┗ 📁rabbitmq //MQTT를 사용하기위한 모듈
        ┗ 📁slack //slack을 사용하기위한 모듈
        ┗ 📁weather_api //날씨API를 사용하기위한 모듈
	┗ 📃programstart_manager.py //각 프로그램 총괄관리
	┗ 📃backend_process.py //MQTT 명령 처리 프로그램
	┗ 📃realtimedb_connect.py //파이어베이스 RealTimeDB를 접속관리하는 프로그램
	┗ 📃realtimedb.json //RealTimeDB에 현황을 파일로 실시간 업데이트
```



___



### programstart_manager

목적 : 백엔드 프로그램 총괄, 하위 프로그램 실행관리, 예외상황 발생처리, 서버 디바이스 모니터링 관리

Python3 로 작성되었으며, 의존 모듈은 아래와 같습니다.

```python
import os
import threading
import time

from module.slack import slack
```



---



### realtimedb_connect

목적 : 실시간DB 접근/관리, 날씨API로부터 데이터 수신

Python3 로 작성되었으며, 의존 모듈은 아래와 같습니다.

```python
import time
import json

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from module.weather_api import openweathermap_api
from module.slack import slack
```



---



### backend_process

목적 : MQTT 클라이언트(송신/수신), 파이어스토어 접근/관리, MQTT 및 파이어스토어 데이터 정제 및 처리

Python3 로 작성되었으며, 의존 모듈은 아래와 같습니다.

```python
import time
import threading
import json

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from module.rabbitmq import rabbitmq_clinet
	┗ include pika
from module.slack import slack
   	┗ include requests
```

