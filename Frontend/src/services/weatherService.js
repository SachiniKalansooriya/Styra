import apiService from './apiService';

class WeatherService {
  // Get current weather
  async getCurrentWeather(location = null) {
    try {
      const params = location ? { location } : {};
      return await apiService.get('/weather/current', params);
    } catch (error) {
      throw new Error(`Failed to get current weather: ${error.message}`);
    }
  }

  // Get weather forecast
  async getWeatherForecast(location = null, days = 5) {
    try {
      const params = { days, ...(location && { location }) };
      return await apiService.get('/weather/forecast', params);
    } catch (error) {
      throw new Error(`Failed to get weather forecast: ${error.message}`);
    }
  }

  // Get weather-based outfit suggestions
  async getWeatherBasedOutfits(weatherData) {
    try {
      return await apiService.post('/weather/outfit-suggestions', weatherData);
    } catch (error) {
      throw new Error(`Failed to get weather-based outfits: ${error.message}`);
    }
  }
}

export default new WeatherService();
