import apiService from './apiService';

class WeatherService {
  // Get current weather by coordinates
  async getCurrentWeather(latitude, longitude) {
    try {
      return await apiService.get(`/api/weather/${latitude}/${longitude}`);
    } catch (error) {
      throw new Error(`Failed to get current weather: ${error.message}`);
    }
  }

  // Get current weather by location object
  async getCurrentWeatherByLocation(location) {
    try {
      if (location && location.latitude && location.longitude) {
        return await this.getCurrentWeather(location.latitude, location.longitude);
      } else {
        throw new Error('Location coordinates are required');
      }
    } catch (error) {
      throw new Error(`Failed to get current weather: ${error.message}`);
    }
  }

  // Get weather forecast (placeholder for future implementation)
  async getWeatherForecast(latitude, longitude, days = 5) {
    try {
      // For now, just get current weather
      // TODO: Implement forecast endpoint in backend
      return await this.getCurrentWeather(latitude, longitude);
    } catch (error) {
      throw new Error(`Failed to get weather forecast: ${error.message}`);
    }
  }

  // Get weather-based outfit suggestions (placeholder)
  async getWeatherBasedOutfits(weatherData) {
    try {
      // This would be handled by the outfit recommendation endpoint
      // that already includes weather data
      return await apiService.post('/api/outfit/ai-recommendation', weatherData);
    } catch (error) {
      throw new Error(`Failed to get weather-based outfits: ${error.message}`);
    }
  }
}

export default new WeatherService();
