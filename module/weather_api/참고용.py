
class WeatherAPI:
    weather_get_interval = 3600 # n초마다 작업진행
    weather_get_last_time = time.time() - weather_get_interval

    def check_timeing(self):
        now_interval = time.time() - self.weather_get_last_time
        if now_interval >= self.weather_get_interval:
            return True
        else:
            return False

    def get_weather(self, px, py):
        # 시간 경과 확인
        if self.check_timeing():
            # API를 통해 날씨정보를 받아옴 (return: JSON)
            try:
                weather_json = weather_api.getUltraSrtNcst(px, py)
                self.weather_get_last_time = time.time()
            except Exception as e:
                alert_error('data.error.error',
                            'ERROR : 날씨API로 부터 값을 받아오는 도중 에러가 발생했습니다. 확인이 필요합니다. *오류명 : ' + str(e))
                return False
            return weather_json
        else:
            return False

    def send_weather(self, send_json_data):
        # JSON 데이터가 왔는지 확인
        if send_json_data == False:
            print("json 데이터가 아니므로 종료")
            return False

        # 기존 메세지 소비
        try:
            method_frame = True
            while method_frame: # 새로운 메세지가 있는지 확인 (do-while)
                method_frame, header_frame, body = wa_channel_direct.basic_get(queue='data.weatherapi', auto_ack=True)
                if body == None: # Queue에 메세지가 없을 경우 예외처리
                    break
        except Exception as e :
            alert_error('data.error.error',
                        "ERROR : data.weatherapi 큐에 메세지를 소비하는 중에 에러가 발생했습니다. 확인이 필요합니다. *오류명 : " + str(e))
            time.sleep(0.01)

        # 새로운 날씨API 데이터 발행
        wa_channel.publish_exchange('webos.topic', 'data.weatherapi.info', send_json_data)
