// services/buyRecommendationService.js
const API_BASE_URL = 'http://172.20.10.7:8000';

const buyRecommendationService = {
  async getBuyingRecommendations(userId = 1) {
    try {
      console.log('Fetching buying recommendations for user:', userId);
      
      const response = await fetch(`${API_BASE_URL}/api/recommendations/buy`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId
        })
      });

      const data = await response.json();
      
      if (response.ok && data.status === 'success') {
        console.log('Buying recommendations received:', data.recommendations);
        return {
          success: true,
          recommendations: data.recommendations || [],
          analytics: data.analytics || {}
        };
      } else {
        console.error('Error from recommendations API:', data);
        return {
          success: false,
          error: data.message || 'Failed to get recommendations',
          recommendations: []
        };
      }
    } catch (error) {
      console.error('Error fetching buying recommendations:', error);
      return {
        success: false,
        error: 'Network error: Could not connect to recommendation service',
        recommendations: []
      };
    }
  },

  // Mock data for testing when backend is not available
  getMockRecommendations() {
    return {
      success: true,
      recommendations: [
        {
          id: 1,
          item_type: 'denim jacket',
          category: 'outerwear',
          reason: 'You have many casual tops but lack versatile outerwear pieces. A denim jacket would complement your existing t-shirts and casual wear.',
          priority: 'high',
          estimated_price: '$45-80',
          color_suggestions: ['classic blue', 'black', 'white'],
          style_match: 85
        },
        {
          id: 2,
          item_type: 'office red trousers',
          category: 'bottoms',
          reason: 'You have several white and black tops that would pair perfectly with red trousers for a professional yet stylish office look.',
          priority: 'medium',
          estimated_price: '$35-60',
          color_suggestions: ['burgundy red', 'deep red', 'crimson'],
          style_match: 78
        },
        {
          id: 3,
          item_type: 'white sneakers',
          category: 'shoes',
          reason: 'Your wardrobe lacks casual footwear. White sneakers are versatile and would work with most of your casual outfits.',
          priority: 'medium',
          estimated_price: '$50-120',
          color_suggestions: ['white', 'off-white'],
          style_match: 82
        },
        {
          id: 4,
          item_type: 'black blazer',
          category: 'outerwear',
          reason: 'A black blazer would instantly elevate your wardrobe and provide formal options for your existing pants and shirts.',
          priority: 'high',
          estimated_price: '$60-150',
          color_suggestions: ['black', 'navy blue'],
          style_match: 90
        }
      ],
      analytics: {
        wardrobe_gaps: ['outerwear', 'formal wear'],
        style_preference: 'casual-professional',
        most_needed: 'versatile pieces',
        budget_recommendation: '$200-400 for complete wardrobe upgrade'
      }
    };
  }
};

export default buyRecommendationService;
