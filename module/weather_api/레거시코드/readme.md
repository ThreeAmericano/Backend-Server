# weather_api 모듈

20201-08-11, 작성자 : 최현식



### 용도

날씨API를 이용하여 현재 날씨상황을 확인하는 용도입니다. 파이썬에서 기본적으로 제공하는 `urllib.request`, `json`, `datetime` 모듈에 의존성이 있습니다.



### 예시

```python
# 위도,경도가 60,128인 지역에 날씨값을 반환합니다.
print(getUltraSrtNcst("60","128"))

# [반환데이터 예시]
# {"PTY":"0","REH":"89","RN1":"0","T1H":"24.1","UUU":"-1.3","VEC":"43","VVV":"-1.4","WSD":"2.1"}
```



## 날씨 API 함수

모두 개체(class)가 아닌 함수로 이루어져있습니다.




__getUltraSrtNcst__ (nx,ny)

​	x,y 좌표를 기준으로 하여 해당 지역에 날씨현황을 반환받습니다.

- nx : 날씨를 확인할 지역에 위도값을 입력합니다.
- ny : 날씨를 확인할 지역에 경도값을 입력합니다.

- return : `json`





##  JSON 데이터 해석

| 항목값 |    항목명    |  단위  | 압축Bit |
| :----: | :----------: | :----: | :-----: |
|  T1H   |     기온     |   ℃    |   10    |
|  RN1   | 1시간 강수량 |   mm   |    8    |
|  UUU   | 동서바람성분 |  m/s   |   12    |
|  VVV   | 남북바람성분 |  m/s   |   12    |
|  REH   |     습도     |   %    |    8    |
|  PTY   |   강수형태   | 코드값 |    4    |
|  VEC   |     풍향     |  deg   |   10    |
|  WSD   |     풍속     |  m/s   |   10    |



## 지역별 x,y 좌표

별첨된 location_pos.md 파일 참조.

