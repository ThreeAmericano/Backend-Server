#-*-coding:utf-8-*-
# 오픈웨더 날씨아이콘 참조 : https://openweathermap.org/weather-conditions
import urllib.request
import json
import datetime


# 인자로 주어진 값(value)를 기준에 따라 좋음/보통/나쁨/매우나쁨 으로 반환하는 함수
def airpollution_policy(value, good, normal, bad):
	if value <= good:
		return '좋음'
	elif value <= normal:
		return '보통'
	elif value <= bad:
		return '나쁨'
	else:
		return '매우나쁨'


class OpenWeatherAPI:
	openweather_api_url = "https://api.openweathermap.org/data/2.5/"
	__service_key = "none"
	__dict_data = {'갱신일': str(datetime.datetime.now())}
	recent_lon = "none"
	recent_lat = "none"

	def __init__(self, service_key):
		self.__service_key = service_key

	def getter_dict(self):
		return self.__dict_data

	def getter_pos_lat(self):
		return self.recent_lat

	def getter_pos_lon(self):
		return self.recent_lon

	def update_now_auto(self, city):
		self.update_weather_city(city)
		self.update_air_pollution(self.recent_lat, self.recent_lon)

	def update_weather_city(self, city):
		self.__dict_data['갱신일'] = str(datetime.datetime.now())

		# API 요청시 필요한 인수값 정의
		ow_api_url = self.openweather_api_url + "weather"
		payload = "?q=" + city + "&" + "lang=kr&" + "appid=" + self.__service_key
		url_total = ow_api_url + payload

		# API 요청하여 데이터 받기
		req = urllib.request.urlopen(url_total)
		res = req.readline()

		# 받은 값 JSON 형태로 정제후 반환
		items = json.loads(res)
		self.recent_lat = str(items['coord']['lat'])
		self.recent_lon = str(items['coord']['lon'])

		self.__dict_data['도시명'] = items['name']
		self.__dict_data['날씨'] = items['weather'][0]['main']
		self.__dict_data['날씨설명'] = items['weather'][0]['description']
		self.__dict_data['아이콘'] = items['weather'][0]['icon']

		self.__dict_data['현재온도'] = str(int(items['main']['temp'])-273.15)[0:4]
		self.__dict_data['체감온도'] = str(int(items['main']['feels_like'])-273.15)[0:4]
		self.__dict_data['최저온도'] = str(int(items['main']['temp_min'])-273.15)[0:4]
		self.__dict_data['최고온도'] = str(int(items['main']['temp_max'])-273.15)[0:4]

		self.__dict_data['습도'] = str(items['main']['humidity']) + "%"
		self.__dict_data['기압'] = str(items['main']['pressure']) + "hPa"
		self.__dict_data['가시거리'] = items['visibility']

		self.__dict_data['풍속'] = str(items['wind']['speed']) + "m/s"
		self.__dict_data['풍향'] = str(items['wind']['deg']) + "도"
		# self.__dict_data['돌풍'] = items['wind']['gust']
		# self.__dict_data['1시간강수'] = items['rain']['1h']) #비 올때만 생김
		# self.__dict_data['3시간강수'] = items['rain']['3h']) #비 올때만 생김
		# self.__dict_data['1시간적설'] = items['snow']['1h']) #눈 올때만 생김
		# self.__dict_data['3시간적설'] = items['snow']['3h']) #눈 올때만 생김
		self.__dict_data['흐림'] = str(items['clouds']['all']) + "%"
		self.__dict_data['일출'] = items['sys']['sunrise']
		self.__dict_data['일몰'] = items['sys']['sunset']

		# 미세먼지 값 불러오기 (대기상태)

	def update_air_pollution(self, pos_lat, pos_lon):
		self.__dict_data['갱신일'] = str(datetime.datetime.now())

		# API 요청시 필요한 인수값 정의
		ow_api_url = self.openweather_api_url + "air_pollution"
		payload = "?lat=" + pos_lat + "&" +\
					"lon=" + pos_lon + "&" +\
					"appid=" + self.__service_key
		url_total = ow_api_url + payload

		# API 요청하여 데이터 받기
		req = urllib.request.urlopen(url_total)
		res = req.readline()

		# 받은 값 JSON 형태로 정제후 반환
		items = json.loads(res)

		# 대기질 기준 : https://www.airkorea.or.kr/web/khaiInfo?pMENU_NO=129
		# air_co = airpollution_policy(items['list'][0]['components']['co'], 16, 36, 76)
		# air_no2 = airpollution_policy(items['list'][0]['components']['no2'], 0.031, 0.061, 0.201)
		air_total = airpollution_policy(items['list'][0]['main']['aqi'], 1, 2, 3)
		air_pm25 = airpollution_policy(items['list'][0]['components']['pm2_5'], 15, 35, 75)
		air_pm10 = airpollution_policy(items['list'][0]['components']['pm10'], 30, 80, 150)
		# air_o3 = airpollution_policy(items['list'][0]['components']['o3'], 0.031, 0.061, 0.201)
		# air_so2 = airpollution_policy(items['list'][0]['components']['so2'], 0.031, 0.061, 0.201)

		self.__dict_data['대기질지수'] = air_total
		self.__dict_data['미세먼지'] = air_pm10
		self.__dict_data['초미세먼지'] = air_pm25
		self.__dict_data['co'] = items['list'][0]['components']['co']
		self.__dict_data['no'] = items['list'][0]['components']['no']
		self.__dict_data['no2'] = items['list'][0]['components']['no2']
		self.__dict_data['o3'] = items['list'][0]['components']['o3']
		self.__dict_data['so2'] = items['list'][0]['components']['so2']
		self.__dict_data['pm2_5'] = items['list'][0]['components']['pm2_5']
		self.__dict_data['pm10'] = items['list'][0]['components']['pm10']
		self.__dict_data['nh3'] = items['list'][0]['components']['nh3']


if __name__ == "__main__":
	ow = OpenWeatherAPI("c7446d3b017961049805343e08347b43")
	ow.update_now_auto("Seoul")
	ow_dict = ow.getter_dict()

	for key in ow_dict:
		print(key + " : %r" % ow_dict[key])
