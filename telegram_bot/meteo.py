import os
from os import getenv
from dotenv import load_dotenv
import requests

load_dotenv()

geo_url = os.getenv('GEO_URL')
weather_url = os.getenv('WEATHER_URL')


class WeatherServiceException(Exception):
    pass


class WeatherService:

    @staticmethod
    def get_geo_data(city_name):
        params = {
            'name': city_name
        }
        res = requests.get(f'{geo_url}', params=params)
        if res.status_code != 200:
            raise WeatherServiceException('Cannot get geo data')
        elif not res.json().get('results'):
            raise WeatherServiceException('City no found')
        return res.json().get('results')

    @staticmethod
    def get_current_weather(lat, lon):
        params = {
            'latitude': lat,
            'longitude': lon,
            'current_weather': True
        }
        res = requests.get(f'{weather_url}', params=params)
        if res.status_code != 200:
            raise WeatherServiceException('Cannot get geo data')
        return res.json().get('current_weather')