# 파이어베이스 Python SDK

파이어베이스 ADMIN SDK를 이용하여 Python언어로 제어하는 것을 다룹니다.

<br>

## 사전작업

### python용 firebase 라이브러리 다운로드

```bash
$ pip3 install firebase-admin
```

<br>

### Firebase로 부터 python용 KEY값 부여받기

Firebase > Project > SidePannel메뉴 중 톱니바퀴 모양 클릭 > 프로젝트 설정 > 서비스 계정 > Firebase Admin SDK > Python > 새 비공개 키 생성

관련 KEY 파일이 .json 형태의 파일로 다운받아짐.

<br>

## Firebase 관련 python 예제

공식자료 : https://firebase.google.com/docs/firestore/quickstart?hl=ko

<br>

###  필수모듈

아래 모듈은 Python으로 파이어베이스에 접근하기위해서 필수로 필요합니다.

```python
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
```

<br>

### Firebase 연결 생성하기

아래 예제를 통해 파이어베이스의 Firestore로 연결을 생성할 수 있습니다.

```python
#Firebase database 인증 및 앱 초기화
print("==========[Init]==========")
cred = credentials.Certificate('threeamericano-firebase-adminsdk-ejh8q-d74c5b0c68.json')
firebase_admin.initialize_app(cred, {
	'projectID': 'threeamericano',
})
db = firestore.client()
```

<br>

### 데이터 쓰기

아래 예제를 통해 `thisistest` 컬렉션에 `id` 문서에 데이터를 만듭니다. (새로 갱신됨)

```python
#데이터 쓰기
print("==========[Write]==========")
doc_ref = db.collection(u'thisistest').document(u'id')
doc_ref.set({
    u'level': 20,
    u'money': 700,
    u'job': "knight"
})
```

<br>

### 데이터 읽기

아래 예제를 통해 `thisistest` 컬렉션에 데이터를 모두 불러옵니다. (딕셔너리 형식)

```python
#데이터 읽기
print("==========[Read]==========")
users_ref = db.collection(u'thisistest')
docs = users_ref.stream()

for doc in docs:
    print(u'{} => {}'.format(doc.id, doc.to_dict()))
```

<br>

---

### 리스너 사용하기

**[FireStore - Python]**

```python
callback_done = threading.Event()
def on_snapshot(doc_snapshot, changes, read_time):
     for doc in doc_snapshot:
         print('Received document snapshot: {0}' . format(doc.id))
     callback_done.set()

col_query = db.collection(u'city')
doc_watch = col_query.on_snapshot(on_snapshot)
```

**[RealTimeDB - Python]**

```python
def yoyoyo(args):
    print(args)
    print("hi")

rtdb = db.reference()
rtdb.listen(yoyoyo)
```



