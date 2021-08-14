#-*-coding:utf-8-*-
# 오픈웨더 날씨아이콘 참조 : https://openweathermap.org/weather-conditions
import urllib.request
import json
import datetime

openweather_api_url = "https://api.openweathermap.org/data/2.5/"
service_key = "c7446d3b017961049805343e08347b43"

dict_data = {'갱신일': str(datetime.datetime.now())}


def getterDict():
	global dict_data
	return dict_data


def __airpollution_policy(value, good, normal, bad):
	if value <= good:
		return '좋음'
	elif value <= normal:
		return '보통'
	elif value <= bad:
		return '나쁨'
	else:
		return '매우나쁨'


def getNowCity(city) :
	global openweather_api_url, service_key, dict_data
	dict_data['갱신일'] = str(datetime.datetime.now())

	# API 요청시 필요한 인수값 정의
	ow_api_url = openweather_api_url + "weather"
	payload = "?q=" + city + "&" + "lang=kr&" + "appid=" + service_key
	url_total = ow_api_url + payload

	# API 요청하여 데이터 받기
	req = urllib.request.urlopen(url_total)
	res = req.readline()

	# 받은 값 JSON 형태로 정제후 반환
	items = json.loads(res)
	dict_data['도시명'] = items['name']
	dict_data['날씨'] = items['weather'][0]['main']
	dict_data['날씨설명'] = items['weather'][0]['description']
	dict_data['아이콘'] = items['weather'][0]['icon']

	dict_data['현재온도'] = str(int(items['main']['temp'])-273.15)[0:4]
	dict_data['체감온도'] = str(int(items['main']['feels_like'])-273.15)[0:4]
	dict_data['최저온도'] = str(int(items['main']['temp_min'])-273.15)[0:4]
	dict_data['최고온도'] = str(int(items['main']['temp_max'])-273.15)[0:4]

	dict_data['습도'] = str(items['main']['humidity']) + "%"
	dict_data['기압'] = str(items['main']['pressure']) + "hPa"
	dict_data['가시거리'] = items['visibility']

	dict_data['풍속'] = str(items['wind']['speed']) + "m/s"
	dict_data['풍향'] = str(items['wind']['deg']) + "도"
	#dict_data['돌풍'] = items['wind']['gust']
	#dict_data['1시간강수'] = items['rain']['1h']) #비 올때만 생김
	#dict_data['3시간강수'] = items['rain']['3h']) #비 올때만 생김
	#dict_data['1시간적설'] = items['snow']['1h']) #눈 올때만 생김
	#dict_data['3시간적설'] = items['snow']['3h']) #눈 올때만 생김
	dict_data['흐림'] = str(items['clouds']['all']) + "%"
	dict_data['일출'] = items['sys']['sunrise']
	dict_data['일몰'] = items['sys']['sunset']

	# 미세먼지 값 불러오기 (대기상태)
	getNowAirPollution(str(items['coord']['lat']), str(items['coord']['lon']))


def getNowAirPollution(pos_lat, pos_lon):
	global openweather_api_url, service_key, dict_data
	dict_data['갱신일'] = str(datetime.datetime.now())

	# API 요청시 필요한 인수값 정의
	ow_api_url = openweather_api_url + "air_pollution"
	payload = "?lat=" + pos_lat + "&" +\
				"lon=" + pos_lon + "&" +\
				"appid=" + service_key
	url_total = ow_api_url + payload

	# API 요청하여 데이터 받기
	req = urllib.request.urlopen(url_total)
	res = req.readline()

	# 받은 값 JSON 형태로 정제후 반환
	items = json.loads(res)

	# 대기질 기준 : https://www.airkorea.or.kr/web/khaiInfo?pMENU_NO=129
	#air_co = airpollution_policy(items['list'][0]['components']['co'], 16, 36, 76)
	#air_no2 = airpollution_policy(items['list'][0]['components']['no2'], 0.031, 0.061, 0.201)
	air_total = __airpollution_policy(items['list'][0]['main']['aqi'], 1, 2, 3)
	air_pm25 = __airpollution_policy(items['list'][0]['components']['pm2_5'], 15, 35, 75)
	air_pm10 = __airpollution_policy(items['list'][0]['components']['pm10'], 30, 80, 150)
	#air_o3 = airpollution_policy(items['list'][0]['components']['o3'], 0.031, 0.061, 0.201)
	#air_so2 = airpollution_policy(items['list'][0]['components']['so2'], 0.031, 0.061, 0.201)

	dict_data['대기질지수'] = air_total
	dict_data['미세먼지'] = air_pm10
	dict_data['초미세먼지'] = air_pm25
	dict_data['co'] = items['list'][0]['components']['co']
	dict_data['no'] = items['list'][0]['components']['no']
	dict_data['no2'] = items['list'][0]['components']['no2']
	dict_data['o3'] = items['list'][0]['components']['o3']
	dict_data['so2'] = items['list'][0]['components']['so2']
	dict_data['pm2_5'] = items['list'][0]['components']['pm2_5']
	dict_data['pm10'] = items['list'][0]['components']['pm10']
	dict_data['nh3'] = items['list'][0]['components']['nh3']


if __name__ == "__main__":
	print("main")
	getNowCity("Incheon")

	for key in dict_data:
		print(key + " : %r" % dict_data[key])

