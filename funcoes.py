import requests
from datetime import datetime, timedelta
import geocoder

class LocalizacaoAutomatica:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.lat = None
            cls._instance.lon = None
            cls._instance.cidade = None
            cls._instance.estado = None
            cls._instance.pais = None
            localizacao = geocoder.ip('me')
            if localizacao.ok:
                cls._instance.lat, cls._instance.lon = localizacao.latlng
                cls._instance.cidade = localizacao.city
                cls._instance.estado = localizacao.state
                cls._instance.pais = localizacao.country
            else:
                print('Não foi possível obter a localização automaticamente.')
        return cls._instance

    def obter_localizacao(self):
        return f'{self.cidade},{self.estado},{self.pais}'

    def obter_cidade(self):
        return self.cidade

    def obter_estado(self):
        return self.estado

    def obter_pais(self):
        return self.estado

    def obter_lat(self):
        return self.lat

    def obter_lon(self):
        return self.lon


class WeatherDataCollector:
    _instance = None

    def __new__(cls, api_key):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.api_key = api_key
        return cls._instance

    def collect_weather_data(self, city):
        endpoint = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric"
        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            data = response.json()
            temperature = data["main"]["temp"]
            conditions = data["weather"][0]["description"]
            return {"temperature": temperature, "conditions": conditions}
        except requests.exceptions.RequestException as e:
            print(f"Erro ao coletar dados: {e}")
            return None


class HistoricalWeatherDataFetcher:
    _instance = None

    def __new__(cls, api_key):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.api_key = api_key
            cls._instance.base_url = 'http://api.openweathermap.org/data/2.5/onecall/timemachine'
        return cls._instance

    def collect_historical_weather(self, lat, lon, date):
        url = f'{self.base_url}?lat={lat}&lon={lon}&dt={date}&appid={self.api_key}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            temperature = data["current"]["temp"]
            conditions = data["current"]["weather"][0]["description"]
            return {"temperature": temperature, "conditions": conditions}
        except requests.exceptions.RequestException as e:
            print(f"Erro ao coletar dados históricos: {e}")
            return None



class WeeklyForecastDataFetcher:
    _instance = None

    def __new__(cls, api_key):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.api_key = api_key
            cls._instance.base_url = 'http://api.openweathermap.org/data/2.5/forecast'
        return cls._instance

    def collect_weekly_forecast(self, city, country):
        url = f'{self.base_url}?q={city},{country}&appid={self.api_key}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            daily_forecasts = [forecast for forecast in data['list'] if forecast['dt_txt'].split()[1] == '12:00:00']
            weekly_forecast = [
                {
                    "date": datetime.fromisoformat(forecast['dt_txt']),
                    "temperature": round(forecast['main']['temp'] - 273.15),
                    "conditions": forecast['weather'][0]['description']
                }
                for forecast in daily_forecasts
            ]
            return weekly_forecast
        except requests.exceptions.RequestException as e:
            print(f"Erro ao coletar dados: {e}")
            return None

#não tem singleton
class WeeklyForecast:
    def __init__(self, weekly_forecast_data):
        self.weekly_forecast_data = weekly_forecast_data

    @staticmethod
    def get_weekly_forecast(data_fetcher, city, country):
        weekly_forecast_data = data_fetcher.collect_weekly_forecast(city, country)
        return WeeklyForecast(weekly_forecast_data)


class WeatherInfo:
    _instance = None

    def __new__(cls, root):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.root = root
            cls._instance.api_key = '95a2aebd33fc348608c9f6d3ace9c548'
            cls._instance.weather_collector = WeatherDataCollector(cls._instance.api_key)
            cls._instance.weekly_data_fetcher = WeeklyForecastDataFetcher(cls._instance.api_key)
            cls._instance.city_usuario, cls._instance.country_usuario, cls._instance.lat_usuario, cls._instance.lon_usuario = cls.get_user_location()
            cls._instance.city_data = cls._instance.weather_collector.collect_weather_data(f"{cls._instance.city_usuario},{cls._instance.country_usuario}")
            cls._instance.weekly_forecast_data = WeeklyForecast.get_weekly_forecast(cls._instance.weekly_data_fetcher, cls._instance.city_usuario, cls._instance.country_usuario)
        return cls._instance

    @staticmethod
    def get_user_location():
        localizacao_obj = LocalizacaoAutomatica()
        resultado = localizacao_obj.obter_localizacao()
        city = localizacao_obj.obter_cidade()
        country = localizacao_obj.obter_pais()
        lat = localizacao_obj.obter_lat()
        lon = localizacao_obj.obter_lon()
        return city, country, lat, lon

    def get_historical_data(self):
        historical_data_fetcher = HistoricalWeatherDataFetcher(self.api_key)
        historical_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        historical_data = historical_data_fetcher.collect_historical_weather(self.lat_usuario, self.lon_usuario, historical_date)
        return historical_data

    def get_weekly_forecast_data(self):
        return self.weekly_forecast_data

    def get_city_data(self):
        return self.city_data

    def search_city(self, city_and_country):
        city_and_country = city_and_country.split(",")
        if len(city_and_country) == 2:
            self.city_usuario, self.country_usuario = map(str.strip, city_and_country)
            self.city_data = self.weather_collector.collect_weather_data(f"{self.city_usuario},{self.country_usuario}")
            self.weekly_forecast_data = WeeklyForecast.get_weekly_forecast(self.weekly_data_fetcher, self.city_usuario, self.country_usuario)
            ResultWindow(self.root, self.city_data, self.weekly_forecast_data)
        else:
            messagebox.showwarning("Aviso", "Por favor, insira a cidade e o país separados por vírgula.")



class WeeklyForecast:
    @staticmethod
    def get_weekly_forecast(data_fetcher, city, country):
        weekly_forecast_data = data_fetcher.collect_weekly_forecast(city, country)
        return weekly_forecast_data