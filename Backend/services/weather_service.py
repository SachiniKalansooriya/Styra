# services/weather_service.py
import requests
import os
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self):
        self.openweather_api_key = os.getenv('OPENWEATHER_API_KEY')
        self.weatherapi_key = os.getenv('WEATHERAPI_KEY')  # Optional alternative
        self.cache = {}
        self.cache_duration = 30 * 60  # 30 minutes
    
    def get_current_weather(self, lat: float, lon: float) -> Dict:
        """Get current weather with fallback to multiple APIs"""
        cache_key = f"{lat},{lon},current"
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        # Try OpenWeatherMap first
        if self.openweather_api_key:
            try:
                weather_data = self._get_openweather_current(lat, lon)
                self._cache_result(cache_key, weather_data)
                return weather_data
            except Exception as e:
                logger.warning(f"OpenWeatherMap failed: {e}")
        
        # Try WeatherAPI as backup
        if self.weatherapi_key:
            try:
                weather_data = self._get_weatherapi_current(lat, lon)
                self._cache_result(cache_key, weather_data)
                return weather_data
            except Exception as e:
                logger.warning(f"WeatherAPI failed: {e}")
        
        # Try Open-Meteo (no API key required)
        try:
            weather_data = self._get_open_meteo_current(lat, lon)
            self._cache_result(cache_key, weather_data)
            return weather_data
        except Exception as e:
            logger.warning(f"Open-Meteo failed: {e}")
        
        # Return fallback data
        logger.info("Using fallback weather data")
        return self._get_fallback_weather()
    
    def _get_openweather_current(self, lat: float, lon: float) -> Dict:
        """Get weather from OpenWeatherMap"""
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.openweather_api_key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            'temperature': round(data['main']['temp']),
            'feels_like': round(data['main']['feels_like']),
            'condition': data['weather'][0]['description'],
            'humidity': data['main']['humidity'],
            'windSpeed': round(data['wind'].get('speed', 0) * 3.6),
            'precipitation': data.get('rain', {}).get('1h', 0),
            'visibility': data.get('visibility', 10000) / 1000,
            'icon': data['weather'][0]['icon'],
            'location': {
                'name': data.get('name', 'Unknown'),
                'country': data['sys'].get('country', 'Unknown')
            },
            'api_source': 'openweathermap',
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_weatherapi_current(self, lat: float, lon: float) -> Dict:
        """Get weather from WeatherAPI.com"""
        url = "https://api.weatherapi.com/v1/current.json"
        params = {
            'key': self.weatherapi_key,
            'q': f"{lat},{lon}",
            'aqi': 'no'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            'temperature': round(data['current']['temp_c']),
            'feels_like': round(data['current']['feelslike_c']),
            'condition': data['current']['condition']['text'],
            'humidity': data['current']['humidity'],
            'windSpeed': round(data['current']['wind_kph']),
            'precipitation': data['current']['precip_mm'],
            'visibility': data['current']['vis_km'],
            'icon': data['current']['condition']['icon'],
            'location': {
                'name': data['location']['name'],
                'country': data['location']['country']
            },
            'api_source': 'weatherapi',
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_open_meteo_current(self, lat: float, lon: float) -> Dict:
        """Get weather from Open-Meteo (free, no API key)"""
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': lat,
            'longitude': lon,
            'current_weather': 'true',
            'hourly': 'temperature_2m,relativehumidity_2m,precipitation,windspeed_10m'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        current = data['current_weather']
        
        # Get additional data from hourly forecast (current hour)
        hourly = data.get('hourly', {})
        current_hour_index = 0  # Simplified - would need proper time matching
        
        return {
            'temperature': round(current['temperature']),
            'feels_like': round(current['temperature']),  # Open-Meteo doesn't provide feels_like
            'condition': self._weather_code_to_description(current['weathercode']),
            'humidity': hourly.get('relativehumidity_2m', [50])[current_hour_index],
            'windSpeed': round(current['windspeed']),
            'precipitation': hourly.get('precipitation', [0])[current_hour_index],
            'visibility': 10,  # Default value
            'icon': self._weather_code_to_icon(current['weathercode']),
            'location': {
                'name': f"Lat: {lat}, Lon: {lon}",
                'country': 'Unknown'
            },
            'api_source': 'open-meteo',
            'timestamp': datetime.now().isoformat()
        }
    
    def _weather_code_to_description(self, code: int) -> str:
        """Convert Open-Meteo weather code to description"""
        code_map = {
            0: "Clear sky",
            1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Fog", 48: "Depositing rime fog",
            51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
            95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail"
        }
        return code_map.get(code, "Unknown")
    
    def _weather_code_to_icon(self, code: int) -> str:
        """Convert Open-Meteo weather code to icon"""
        if code == 0:
            return "01d"  # Clear sky
        elif code in [1, 2]:
            return "02d"  # Partly cloudy
        elif code == 3:
            return "04d"  # Overcast
        elif code in [45, 48]:
            return "50d"  # Fog
        elif code in [51, 53, 55, 61, 63, 65]:
            return "09d"  # Rain
        elif code in [71, 73, 75]:
            return "13d"  # Snow
        elif code in [95, 96, 99]:
            return "11d"  # Thunderstorm
        else:
            return "02d"  # Default
    
    def _cache_result(self, cache_key: str, data: Dict):
        """Cache the weather result"""
        self.cache[cache_key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid"""
        if cache_key not in self.cache:
            return False
        
        cache_time = self.cache[cache_key]['timestamp']
        return (datetime.now() - cache_time).seconds < self.cache_duration
    
    def _get_fallback_weather(self) -> Dict:
        """Return fallback weather data"""
        return {
            'temperature': 22,
            'feels_like': 24,
            'condition': 'partly cloudy',
            'humidity': 55,
            'windSpeed': 12,
            'precipitation': 0,
            'visibility': 10,
            'icon': '02d',
            'location': {
                'name': 'Default Location',
                'country': 'Unknown'
            },
            'api_source': 'fallback',
            'timestamp': datetime.now().isoformat()
        }

# Global instance
weather_service = WeatherService()