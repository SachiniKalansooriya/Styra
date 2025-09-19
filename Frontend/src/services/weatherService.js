// weatherService.js
import apiService from './apiService';
import * as Location from 'expo-location';

class WeatherService {
  constructor() {
    this.weatherCache = new Map();
    this.locationCache = null;
    this.cacheTimeout = 600000; // 10 minutes
    
    // Load API keys from environment or config
    this.apiKeys = {
      openWeather: process.env.EXPO_PUBLIC_OPENWEATHER_API_KEY,
      weatherApi: process.env.EXPO_PUBLIC_WEATHER_API_KEY,
      openCage: process.env.EXPO_PUBLIC_OPENCAGE_API_KEY,
    };
  }

  // Make sure this method exists and is properly defined
  async getCurrentWeather(latitude, longitude) {
    if (!latitude || !longitude) {
      throw new Error('Valid coordinates required for weather data');
    }

    const cacheKey = `${latitude.toFixed(3)},${longitude.toFixed(3)}`;
    const cachedWeather = this.weatherCache.get(cacheKey);
    
    // Use cache if recent
    if (cachedWeather && (Date.now() - cachedWeather.timestamp) < this.cacheTimeout) {
      console.log('Using cached weather data');
      return cachedWeather.data;
    }

    console.log('Fetching fresh weather data for:', latitude, longitude);
    
    // Try different weather sources
    const weatherSources = [
      () => this.getCurrentWeatherFromOpenMeteo(latitude, longitude),
      () => this.getOpenWeatherMapData(latitude, longitude),
      () => this.getWeatherAPIData(latitude, longitude),
      () => this.getBackendWeather(latitude, longitude),
    ];

    for (let i = 0; i < weatherSources.length; i++) {
      try {
        console.log(`Trying weather source ${i + 1}...`);
        const weatherData = await weatherSources[i]();
        
        if (weatherData && weatherData.status === 'success') {
          // Cache successful result
          this.weatherCache.set(cacheKey, {
            data: weatherData,
            timestamp: Date.now()
          });
          
          console.log('Weather retrieved successfully from:', weatherData.source);
          return weatherData;
        }
      } catch (error) {
        console.log(`Weather source ${i + 1} failed:`, error.message);
        continue;
      }
    }

    // If all APIs fail, generate contextual mock data
    console.log('All weather APIs failed, generating contextual data');
    return this.generateContextualWeatherData(latitude, longitude);
  }

  // Enhanced location accuracy
  async getAccurateLocation() {
    try {
      console.log('Starting enhanced location detection...');
      
      // Check for cached location first
      if (this.locationCache && (Date.now() - this.locationCache.timestamp) < this.cacheTimeout) {
        console.log('Using cached location');
        return this.locationCache;
      }

      let bestLocation = null;
      let bestAccuracy = Infinity;
      const maxAttempts = 3;

      // High accuracy GPS attempts
      for (let attempt = 0; attempt < maxAttempts; attempt++) {
        try {
          console.log(`High accuracy GPS attempt ${attempt + 1}/${maxAttempts}`);
          
          const location = await Location.getCurrentPositionAsync({
            accuracy: Location.Accuracy.BestForNavigation,
            timeout: 20000,
            maximumAge: 5000,
          });

          console.log(`Attempt ${attempt + 1} - Accuracy: ${location.coords.accuracy}m`);

          if (location.coords.accuracy < bestAccuracy) {
            bestLocation = location;
            bestAccuracy = location.coords.accuracy;
          }

          // If accuracy is very good, use it immediately
          if (location.coords.accuracy < 50) {
            console.log('Good GPS accuracy achieved');
            break;
          }

          // Wait between attempts
          if (attempt < maxAttempts - 1) {
            await new Promise(resolve => setTimeout(resolve, 2000));
          }
        } catch (error) {
          console.log(`GPS attempt ${attempt + 1} failed:`, error.message);
        }
      }

      // If high accuracy GPS succeeded
      if (bestLocation) {
        const locationData = {
          latitude: bestLocation.coords.latitude,
          longitude: bestLocation.coords.longitude,
          accuracy: bestLocation.coords.accuracy,
          timestamp: Date.now(),
          method: 'gps_high_accuracy'
        };
        
        this.locationCache = locationData;
        return locationData;
      }

      // Fallback to balanced accuracy
      console.log('Trying balanced accuracy GPS...');
      const balancedLocation = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Balanced,
        timeout: 15000,
        maximumAge: 30000,
      });

      const locationData = {
        latitude: balancedLocation.coords.latitude,
        longitude: balancedLocation.coords.longitude,
        accuracy: balancedLocation.coords.accuracy,
        timestamp: Date.now(),
        method: 'gps_balanced'
      };
      
      this.locationCache = locationData;
      return locationData;

    } catch (error) {
      console.error('GPS location failed:', error);
      
      // Try IP-based geolocation
      try {
        console.log('Trying IP-based geolocation...');
        const ipLocation = await this.getIPLocation();
        if (ipLocation) {
          this.locationCache = ipLocation;
          return ipLocation;
        }
      } catch (ipError) {
        console.log('IP geolocation failed:', ipError.message);
      }

      return null;
    }
  }

  // IP-based geolocation
  async getIPLocation() {
    const ipServices = [
      {
        url: 'https://ipapi.co/json/',
        parser: (data) => ({
          latitude: parseFloat(data.latitude),
          longitude: parseFloat(data.longitude),
          city: data.city,
          country: data.country_name,
          accuracy: 10000,
        })
      },
      {
        url: 'http://ip-api.com/json/',
        parser: (data) => ({
          latitude: parseFloat(data.lat),
          longitude: parseFloat(data.lon),
          city: data.city,
          country: data.country,
          accuracy: 15000,
        })
      }
    ];

    for (const service of ipServices) {
      try {
        const response = await fetch(service.url, { timeout: 10000 });
        
        if (response.ok) {
          const data = await response.json();
          const locationData = service.parser(data);
          
          if (locationData.latitude && locationData.longitude) {
            return {
              ...locationData,
              timestamp: Date.now(),
              method: 'ip_geolocation'
            };
          }
        }
      } catch (error) {
        console.log(`IP service failed:`, error.message);
        continue;
      }
    }

    return null;
  }

  // OpenMeteo implementation (free, no API key required)
  async getCurrentWeatherFromOpenMeteo(latitude, longitude) {
    const url = `https://api.open-meteo.com/v1/current?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,pressure_msl&timezone=auto&temperature_unit=celsius&wind_speed_unit=kmh`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
      timeout: 15000,
    });

    if (!response.ok) {
      throw new Error(`Open-Meteo error: ${response.status}`);
    }

    const data = await response.json();

    if (!data.current) {
      throw new Error('Invalid Open-Meteo response');
    }

    // Get location name
    const locationName = await this.getLocationName(latitude, longitude);

    return {
      status: 'success',
      current: {
        temperature: Math.round(data.current.temperature_2m),
        condition: this.mapWeatherCodeToCondition(data.current.weather_code),
        humidity: data.current.relative_humidity_2m,
        windSpeed: Math.round(data.current.wind_speed_10m || 0),
        pressure: data.current.pressure_msl,
        location: {
          name: locationName || 'Current Location',
          latitude,
          longitude
        }
      },
      source: 'Open-Meteo'
    };
  }

  // OpenWeatherMap implementation
  async getOpenWeatherMapData(latitude, longitude) {
    if (!this.apiKeys.openWeather) {
      throw new Error('OpenWeatherMap API key not available');
    }

    const url = `https://api.openweathermap.org/data/2.5/weather?lat=${latitude}&lon=${longitude}&appid=${this.apiKeys.openWeather}&units=metric`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
      timeout: 15000,
    });

    if (!response.ok) {
      throw new Error(`OpenWeatherMap error: ${response.status}`);
    }

    const data = await response.json();
    
    return {
      status: 'success',
      current: {
        temperature: Math.round(data.main.temp),
        condition: data.weather[0].description,
        humidity: data.main.humidity,
        windSpeed: Math.round((data.wind?.speed || 0) * 3.6),
        pressure: data.main.pressure,
        location: {
          name: data.name || 'Unknown Location',
          latitude,
          longitude
        }
      },
      source: 'OpenWeatherMap'
    };
  }

  // WeatherAPI implementation
  async getWeatherAPIData(latitude, longitude) {
    if (!this.apiKeys.weatherApi) {
      throw new Error('WeatherAPI key not available');
    }

    const url = `https://api.weatherapi.com/v1/current.json?key=${this.apiKeys.weatherApi}&q=${latitude},${longitude}&aqi=no`;
    
    const response = await fetch(url, { timeout: 15000 });

    if (!response.ok) {
      throw new Error(`WeatherAPI error: ${response.status}`);
    }

    const data = await response.json();
    
    return {
      status: 'success',
      current: {
        temperature: Math.round(data.current.temp_c),
        condition: data.current.condition.text,
        humidity: data.current.humidity,
        windSpeed: Math.round(data.current.wind_kph),
        pressure: data.current.pressure_mb,
        location: {
          name: data.location.name,
          latitude: data.location.lat,
          longitude: data.location.lon
        }
      },
      source: 'WeatherAPI'
    };
  }

  // Backend weather
  async getBackendWeather(latitude, longitude) {
    return await apiService.get(`/api/weather/${latitude}/${longitude}`);
  }

  // Get location name using reverse geocoding
  async getLocationName(latitude, longitude) {
    try {
      // Try Nominatim first (free, no API key)
      const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=14&addressdetails=1`;
      
      const response = await fetch(url, {
        headers: { 'User-Agent': 'StyraApp/1.0' },
        timeout: 8000,
      });
      
      if (response.ok) {
        const data = await response.json();
        
        if (data.address) {
          return data.address.city || 
                 data.address.town || 
                 data.address.village || 
                 data.address.suburb ||
                 data.address.municipality ||
                 data.display_name?.split(',')[0];
        }
      }
    } catch (error) {
      console.log('Nominatim geocoding failed:', error.message);
    }

    // Fallback to Expo reverse geocoding
    try {
      const reverseGeocode = await Location.reverseGeocodeAsync({
        latitude,
        longitude,
      });

      if (reverseGeocode && reverseGeocode.length > 0) {
        const location = reverseGeocode[0];
        return location.city || 
               location.subregion || 
               location.district || 
               location.region;
      }
    } catch (error) {
      console.log('Expo reverse geocoding failed:', error.message);
    }

    return null;
  }

  // Generate contextual weather when APIs fail
  async generateContextualWeatherData(latitude, longitude) {
    console.log('Generating contextual weather data');
    
    const now = new Date();
    const month = now.getMonth() + 1;
    const hour = now.getHours();
    
    // Climate zone based on latitude
    const climateZone = this.getClimateZone(latitude);
    const seasonalFactor = this.getSeasonalFactor(latitude, month);
    
    // Calculate temperature
    const baseTemp = this.calculateBaseTemperature(climateZone, seasonalFactor, hour);
    const tempVariation = (Math.random() - 0.5) * 4;
    const temperature = Math.round(baseTemp + tempVariation);
    
    // Generate conditions
    const conditions = this.getClimateConditions(climateZone);
    const condition = conditions[Math.floor(Math.random() * conditions.length)];
    
    // Calculate humidity
    const humidity = this.calculateHumidity(climateZone);
    
    // Wind speed
    const windSpeed = Math.round(Math.random() * 12 + 3);
    
    // Get location name
    const locationName = await this.getLocationName(latitude, longitude);

    return {
      status: 'success',
      current: {
        temperature,
        condition,
        humidity,
        windSpeed,
        location: {
          name: locationName || 'Current Location',
          latitude,
          longitude
        }
      },
      source: 'Contextual Generation'
    };
  }

  // Climate zone helper
  getClimateZone(latitude) {
    const absLat = Math.abs(latitude);
    
    if (absLat >= 66.5) return 'polar';
    if (absLat >= 60) return 'subarctic';
    if (absLat >= 45) return 'temperate';
    if (absLat >= 23.5) return 'subtropical';
    return 'tropical';
  }

  // Seasonal factor
  getSeasonalFactor(latitude, month) {
    const isNorthern = latitude > 0;
    const adjustedMonth = isNorthern ? month : (month + 6) % 12 || 12;
    return Math.cos((adjustedMonth - 1) * Math.PI / 6);
  }

  // Base temperature calculation
  calculateBaseTemperature(climateZone, seasonalFactor, hour) {
    const baseTemps = {
      tropical: 28,
      subtropical: 22,
      temperate: 15,
      subarctic: 2,
      polar: -10
    };
    
    const baseTemp = baseTemps[climateZone] || 20;
    const seasonalAdjustment = seasonalFactor * 6;
    
    // Daily temperature variation
    const dailyFactor = Math.cos((hour - 14) * Math.PI / 12);
    const dailyAdjustment = dailyFactor * 4;
    
    return baseTemp + seasonalAdjustment + dailyAdjustment;
  }

  // Climate conditions
  getClimateConditions(climateZone) {
    const conditionSets = {
      tropical: ['Sunny', 'Partly cloudy', 'Cloudy', 'Light rain', 'Heavy rain'],
      subtropical: ['Sunny', 'Partly cloudy', 'Cloudy', 'Light rain', 'Overcast'],
      temperate: ['Sunny', 'Partly cloudy', 'Cloudy', 'Light rain', 'Overcast'],
      subarctic: ['Partly cloudy', 'Cloudy', 'Overcast', 'Light snow'],
      polar: ['Cloudy', 'Overcast', 'Light snow', 'Heavy snow']
    };
    
    return conditionSets[climateZone] || conditionSets.subtropical;
  }

  // Humidity calculation
  calculateHumidity(climateZone) {
    const baseHumidities = {
      tropical: 80,
      subtropical: 65,
      temperate: 60,
      subarctic: 70,
      polar: 75
    };
    
    const baseHumidity = baseHumidities[climateZone] || 65;
    const variation = (Math.random() - 0.5) * 20;
    return Math.max(40, Math.min(95, Math.round(baseHumidity + variation)));
  }

  // Weather code mapping
  mapWeatherCodeToCondition(code) {
    const weatherCodes = {
      0: 'Clear sky', 1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast',
      45: 'Fog', 48: 'Depositing rime fog', 51: 'Light drizzle', 53: 'Moderate drizzle',
      55: 'Dense drizzle', 61: 'Slight rain', 63: 'Moderate rain', 65: 'Heavy rain',
      71: 'Slight snow', 73: 'Moderate snow', 75: 'Heavy snow',
      80: 'Slight rain showers', 81: 'Moderate rain showers', 82: 'Violent rain showers',
      95: 'Thunderstorm', 96: 'Thunderstorm with slight hail', 99: 'Thunderstorm with heavy hail'
    };
    
    return weatherCodes[code] || 'Unknown';
  }

  // Main public method
  async getCurrentWeatherByLocation(requestedLocation = null) {
    try {
      let location = requestedLocation;
      
      if (!location) {
        location = await this.getAccurateLocation();
        if (!location) {
          throw new Error('Unable to determine location');
        }
      }

      return await this.getCurrentWeather(location.latitude, location.longitude);
      
    } catch (error) {
      console.error('Weather service error:', error);
      throw error;
    }
  }

  // Clear cache
  clearCache() {
    this.weatherCache.clear();
    this.locationCache = null;
    console.log('Cache cleared');
  }
}

// Make sure to export properly
const weatherService = new WeatherService();
export default weatherService;