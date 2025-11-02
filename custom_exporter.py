from prometheus_client import start_http_server, Gauge, Info
import requests
import time

# Информация об экспортере
exporter_info = Info('custom_exporter_info', 'Custom API Exporter Info')

# Метрики погоды (Астана)
weather_temperature = Gauge(
    'weather_temperature_celsius',
    'Current temperature in Astana',
    ['city', 'country']
)

weather_windspeed = Gauge(
    'weather_windspeed_kmh',
    'Current wind speed in Astana',
    ['city', 'country']
)

weather_api_status = Gauge(
    'weather_api_status',
    'Weather API status (1=up, 0=down)'
)


def fetch_weather_data():
    """
    Получить данные о погоде в Астане через Open-Meteo API
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': 51.1694,
            'longitude': 71.4491,
            'current_weather': 'true',
            'timezone': 'Asia/Almaty'
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        current = data['current_weather']

        weather_temperature.labels(city='Astana', country='Kazakhstan').set(current['temperature'])
        weather_windspeed.labels(city='Astana', country='Kazakhstan').set(current['windspeed'])
        weather_api_status.set(1)

        return True

    except requests.exceptions.RequestException:
        weather_api_status.set(0)
        return False


if __name__ == '__main__':
    exporter_info.info({
        'version': '1.0',
        'author': 'Begaidar Sailaubayev',
        'sources': 'weather'
    })

    start_http_server(8000)
    print("✅ Custom Exporter started on port 8000")

    while True:
        fetch_weather_data()
        time.sleep(30)
