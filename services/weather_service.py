import requests
from datetime import datetime

class WeatherService:
    def __init__(self, api_key, city):
        self._api_key = api_key
        self._city = city
        self._url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"

    def get_current_weather(self, time : datetime) -> dict:
        try:
            response = requests.get(self._url, timeout= 5)
            response.raise_for_status()

            data = response.json()

            target_timestamp = time.timestamp()

            best_match_weather = None
            min_time = float('inf')
            for entry in data['list']:
                entry_time = entry['dt']
                if abs(target_timestamp - entry_time) < min_time:
                    min_time = abs(target_timestamp - entry_time)
                    best_match_weather = entry
            
            if min_time > 432000:
                return self._default_weather()
            
            temp = best_match_weather['main']['temp']
            wind_kmh = best_match_weather['wind']['speed'] * 3.6
            condition = best_match_weather['weather'][0]['main'].lower()

            is_raining = 1 if condition in ['rain', 'drizzle', 'thunderstorm', 'snow'] else 0
            return {
                "wind_speed" : wind_kmh,
                "temperature" : temp,
                "is_raining" : is_raining
            }
        except requests.exceptions.RequestException as e:
            print(f"API ERROR {e}")
            return self._default_weather()
        
    def _default_weather(self) -> dict:
        return {
                "wind_speed" : 1,
                "temperature" : 20,
                "is_raining" : 0
            }

