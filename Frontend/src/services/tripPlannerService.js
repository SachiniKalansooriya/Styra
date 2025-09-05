// services/tripPlannerService.js
import apiService from './apiService';
import wardrobeService from './wardrobeService';

class TripPlannerService {
  async generateSmartPackingList(tripDetails) {
    try {
      // Get user's wardrobe items
      const wardrobeItems = await wardrobeService.getWardrobeItems();
      
      // Calculate trip duration
      const duration = Math.ceil((tripDetails.endDate - tripDetails.startDate) / (1000 * 60 * 60 * 24));
      
      // Generate packing list based on wardrobe and trip requirements
      const packingList = this.createIntelligentPackingList(tripDetails, wardrobeItems, duration);
      
      // Try to get enhanced recommendations from backend
      try {
        const backendResponse = await apiService.post('/api/trip-planner/enhanced-packing', {
          tripDetails,
          wardrobeItems,
          duration
        });
        
        if (backendResponse.status === 'success') {
          return {
            ...packingList,
            recommendations: backendResponse.recommendations,
            wardrobeMatches: backendResponse.wardrobeMatches
          };
        }
      } catch (error) {
        console.log('Backend enhancement failed, using local generation');
      }
      
      return packingList;
    } catch (error) {
      console.error('Error generating smart packing list:', error);
      throw error;
    }
  }

  createIntelligentPackingList(tripDetails, wardrobeItems, duration) {
    const { activities, weatherExpected, packingStyle, destination } = tripDetails;
    
    // Categorize existing wardrobe items
    const categorizedWardrobe = this.categorizeWardrobe(wardrobeItems);
    
    // Base requirements calculation
    const baseRequirements = this.calculateBaseRequirements(duration, packingStyle);
    
    // Activity-specific additions
    const activityRequirements = this.getActivityRequirements(activities);
    
    // Weather-specific additions
    const weatherRequirements = this.getWeatherRequirements(weatherExpected);
    
    // Create packing list with wardrobe matches
    return this.createPackingListWithMatches(
      baseRequirements,
      activityRequirements,
      weatherRequirements,
      categorizedWardrobe
    );
  }

  categorizeWardrobe(items) {
    return {
      tops: items.filter(item => item.category === 'tops'),
      bottoms: items.filter(item => item.category === 'bottoms'),
      dresses: items.filter(item => item.category === 'dresses'),
      shoes: items.filter(item => item.category === 'shoes'),
      accessories: items.filter(item => item.category === 'accessories'),
      outerwear: items.filter(item => item.category === 'outerwear')
    };
  }

  calculateBaseRequirements(duration, style) {
    const multipliers = {
      minimal: { tops: 0.7, bottoms: 0.5, dresses: 0.3 },
      comfort: { tops: 1.0, bottoms: 0.6, dresses: 0.4 },
      fashion: { tops: 1.3, bottoms: 0.8, dresses: 0.6 },
      business: { tops: 1.1, bottoms: 0.7, dresses: 0.5 }
    };

    const mult = multipliers[style] || multipliers.comfort;

    return {
      tops: Math.max(2, Math.ceil(duration * mult.tops)),
      bottoms: Math.max(2, Math.ceil(duration * mult.bottoms)),
      dresses: Math.ceil(duration * mult.dresses),
      underwear: duration + 1,
      socks: duration + 1,
      shoes: 2
    };
  }

  getActivityRequirements(activities) {
    const requirements = {
      tops: [],
      bottoms: [],
      shoes: [],
      accessories: [],
      special: []
    };

    activities.forEach(activity => {
      switch (activity) {
        case 'Business Meetings':
          requirements.tops.push('Business shirt/blouse');
          requirements.bottoms.push('Dress pants/skirt');
          requirements.shoes.push('Business shoes');
          requirements.accessories.push('Belt', 'Watch', 'Business bag');
          break;
        
        case 'Beach/Pool':
          requirements.special.push('Swimwear', 'Beach cover-up');
          requirements.shoes.push('Sandals/flip-flops');
          requirements.accessories.push('Sun hat', 'Sunglasses', 'Beach bag');
          break;
        
        case 'Hiking/Outdoor':
          requirements.tops.push('Moisture-wicking shirts');
          requirements.bottoms.push('Hiking pants/shorts');
          requirements.shoes.push('Hiking boots');
          requirements.accessories.push('Backpack', 'Water bottle');
          break;
        
        case 'Fine Dining':
          requirements.tops.push('Elegant shirt/blouse');
          requirements.bottoms.push('Dress pants/elegant dress');
          requirements.shoes.push('Dress shoes');
          requirements.accessories.push('Nice jewelry');
          break;
        
        case 'Nightlife':
          requirements.tops.push('Going-out tops');
          requirements.bottoms.push('Party pants/dress');
          requirements.shoes.push('Party shoes');
          break;
      }
    });

    return requirements;
  }

  getWeatherRequirements(weather) {
    const requirements = {
      tops: [],
      outerwear: [],
      accessories: [],
      special: []
    };

    const weatherLower = weather.toLowerCase();

    if (weatherLower.includes('cold') || weatherLower.includes('winter')) {
      requirements.outerwear.push('Warm jacket/coat', 'Sweaters');
      requirements.accessories.push('Gloves', 'Scarf', 'Warm hat');
    }

    if (weatherLower.includes('rain')) {
      requirements.outerwear.push('Rain jacket');
      requirements.accessories.push('Umbrella');
    }

    if (weatherLower.includes('hot') || weatherLower.includes('summer')) {
      requirements.tops.push('Light, breathable shirts');
      requirements.accessories.push('Sun hat', 'Sunglasses');
    }

    return requirements;
  }

  createPackingListWithMatches(base, activity, weather, wardrobe) {
    const packingList = [];

    // Clothing essentials with wardrobe matches
    packingList.push({
      category: 'Clothing Essentials',
      items: this.createItemsWithMatches([
        { name: `${base.tops} shirts/tops`, type: 'tops', quantity: base.tops },
        { name: `${base.bottoms} pants/bottoms`, type: 'bottoms', quantity: base.bottoms },
        { name: `${base.underwear} underwear`, type: 'underwear', quantity: base.underwear },
        { name: `${base.socks} socks`, type: 'socks', quantity: base.socks }
      ], wardrobe)
    });

    // Activity-specific items
    if (activity.tops.length || activity.bottoms.length || activity.special.length) {
      packingList.push({
        category: 'Activity Specific',
        items: this.createItemsWithMatches([
          ...activity.tops.map(item => ({ name: item, type: 'tops' })),
          ...activity.bottoms.map(item => ({ name: item, type: 'bottoms' })),
          ...activity.special.map(item => ({ name: item, type: 'special' }))
        ], wardrobe)
      });
    }

    // Footwear
    packingList.push({
      category: 'Footwear',
      items: this.createItemsWithMatches([
        { name: 'Comfortable walking shoes', type: 'shoes' },
        ...activity.shoes.map(item => ({ name: item, type: 'shoes' }))
      ], wardrobe)
    });

    // Weather-specific
    if (weather.outerwear.length || weather.accessories.length) {
      packingList.push({
        category: 'Weather Protection',
        items: this.createItemsWithMatches([
          ...weather.outerwear.map(item => ({ name: item, type: 'outerwear' })),
          ...weather.accessories.map(item => ({ name: item, type: 'accessories' }))
        ], wardrobe)
      });
    }

    // Accessories
    const allAccessories = [...new Set([...activity.accessories, ...weather.accessories])];
    if (allAccessories.length) {
      packingList.push({
        category: 'Accessories',
        items: this.createItemsWithMatches(
          allAccessories.map(item => ({ name: item, type: 'accessories' })),
          wardrobe
        )
      });
    }

    // Travel essentials
    packingList.push({
      category: 'Travel Essentials',
      items: [
        { name: 'Passport/ID', wardrobeMatch: null, status: 'required' },
        { name: 'Phone charger', wardrobeMatch: null, status: 'required' },
        { name: 'Toiletries', wardrobeMatch: null, status: 'required' },
        { name: 'Medications', wardrobeMatch: null, status: 'required' }
      ]
    });

    return packingList;
  }

  createItemsWithMatches(items, wardrobe) {
    return items.map(item => {
      const matches = this.findWardrobeMatches(item, wardrobe);
      return {
        name: item.name,
        wardrobeMatches: matches,
        status: matches.length > 0 ? 'available' : 'needed',
        type: item.type,
        quantity: item.quantity || 1
      };
    });
  }

  findWardrobeMatches(item, wardrobe) {
    const category = wardrobe[item.type] || [];
    
    // Simple matching based on category and keywords
    return category.filter(wardrobeItem => {
      const itemName = item.name.toLowerCase();
      const wardrobeName = wardrobeItem.name.toLowerCase();
      const wardrobeCategory = wardrobeItem.category.toLowerCase();
      
      // Direct category match
      if (wardrobeCategory === item.type) return true;
      
      // Keyword matching
      const keywords = itemName.split(' ');
      return keywords.some(keyword => 
        wardrobeName.includes(keyword) || wardrobeCategory.includes(keyword)
      );
    });
  }

  async saveTrip(tripDetails) {
    try {
      const response = await apiService.post('/api/trips', tripDetails);
      return response;
    } catch (error) {
      console.error('Error saving trip:', error);
      throw error;
    }
  }
}

export default new TripPlannerService();