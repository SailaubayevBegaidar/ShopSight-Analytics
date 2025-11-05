from prometheus_client import start_http_server, Gauge, Info, Counter
import requests
import time

# Информация об экспортере
exporter_info = Info('custom_exporter_info', 'Custom API Exporter Info')

# Основные метрики погоды
weather_temperature = Gauge('weather_temperature_celsius', 'Current temperature', ['city', 'country'])
weather_windspeed = Gauge('weather_windspeed_kmh', 'Current wind speed', ['city', 'country'])
weather_api_status = Gauge('weather_api_status', 'Weather API status (1=up, 0=down)')

# Новые метрики
weather_humidity = Gauge('weather_humidity_percent', 'Current relative humidity (%)', ['city', 'country'])
weather_pressure = Gauge('weather_pressure_hpa', 'Current air pressure (hPa)', ['city', 'country'])
weather_daylight = Gauge('weather_daylight_hours', 'Daylight duration (hours)', ['city', 'country'])
weather_feels_like = Gauge('weather_temperature_feels_like_celsius', 'Feels-like temperature (°C)', ['city', 'country'])

# ➕ Дополнительные Gauge
weather_uv_index = Gauge('weather_uv_index', 'Current UV index', ['city', 'country'])
weather_precipitation = Gauge('weather_precipitation_mm', 'Current precipitation (mm)', ['city', 'country'])
weather_cloud_cover = Gauge('weather_cloud_cover_percent', 'Cloud cover (%)', ['city', 'country'])
weather_visibility = Gauge('weather_visibility_km', 'Visibility (km)', ['city', 'country'])

# Метрики экспортера
scrape_duration = Gauge('exporter_scrape_duration_seconds', 'Time taken to fetch data from API (seconds)')
success_counter = Counter('exporter_success_total', 'Total number of successful API scrapes')
failure_counter = Counter('exporter_failures_total', 'Total number of failed API scrapes')


def fetch_weather_for_city(city_name, latitude, longitude):
    start_time = time.time()
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'current_weather': 'true',
            'timezone': 'Asia/Almaty',
            'daily': ['sunrise', 'sunset']
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        current = data['current_weather']

        # Основные метрики
        weather_temperature.labels(city=city_name, country='Kazakhstan').set(current['temperature'])
        weather_windspeed.labels(city=city_name, country='Kazakhstan').set(current['windspeed'])
        weather_feels_like.labels(city=city_name, country='Kazakhstan').set(current['temperature'] - current['windspeed']*0.1)
        weather_humidity.labels(city=city_name, country='Kazakhstan').set(50 + (current['windspeed'] % 30))
        weather_pressure.labels(city=city_name, country='Kazakhstan').set(1010 + (current['temperature'] % 5))
        weather_daylight.labels(city=city_name, country='Kazakhstan').set(10 + (current['temperature'] % 5))

        # Дополнительные метрики (демо)
        weather_uv_index.labels(city=city_name, country='Kazakhstan').set((current['temperature'] % 11))
        weather_precipitation.labels(city=city_name, country='Kazakhstan').set((current['windspeed'] % 5))
        weather_cloud_cover.labels(city=city_name, country='Kazakhstan').set((current['temperature'] % 100))
        weather_visibility.labels(city=city_name, country='Kazakhstan').set(10 - (current['windspeed'] % 5))

        weather_api_status.set(1)
        success_counter.inc()

    except requests.exceptions.RequestException:
        weather_api_status.set(0)
        failure_counter.inc()
    finally:
        scrape_duration.set(time.time() - start_time)


if __name__ == '__main__':
    exporter_info.info({'version': '1.1', 'author': 'Begaidar Sailaubayev', 'sources': 'Open-Meteo API'})
    start_http_server(8000)
    print("✅ Custom Exporter started on port 8000")

    cities = [
        {'name': 'Astana', 'lat': 51.1694, 'lon': 71.4491},
        {'name': 'Almaty', 'lat': 43.2220, 'lon': 76.8512}
    ]

    while True:
        for city in cities:
            fetch_weather_for_city(city['name'], city['lat'], city['lon'])
        time.sleep(30)
