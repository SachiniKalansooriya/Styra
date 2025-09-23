# image_analysis.py - Updated to use deepfashion_analyzer
from services.deepfashion_analyzer import deepfashion_analyzer
import logging

logger = logging.getLogger(__name__)

class AdvancedImageAnalysisService:
    def __init__(self):
        self.primary_analyzer = deepfashion_analyzer
        logger.info("Image analysis service initialized with DeepFashion analyzer")
    
    def analyze_clothing_item(self, image_data: bytes):
        try:
            result = self.primary_analyzer.analyze_clothing_item(image_data)
            logger.info(f"Analysis completed: {result.get('analysis_method', 'unknown')} - confidence: {result.get('confidence', 0):.2f}")
            return result
        except Exception as e:
            logger.error(f"Analysis service error: {e}")
            return {
                'suggestedCategory': 'tops',
                'suggestedColor': 'Unknown',
                'suggestedOccasion': 'casual',
                'confidence': 0.3,
                'analysis_method': 'service_error',
                'error': str(e),
                'success': False
            }
    
    def get_service_info(self):
        try:
            return self.primary_analyzer.get_service_status()
        except Exception as e:
            logger.error(f"Error getting service info: {e}")
            return {
                'ai_models_loaded': False,
                'supported_categories': ['tops', 'bottoms', 'dresses', 'shoes', 'accessories', 'outerwear'],
                'supported_colors': ['Unknown'],
                'analysis_methods': ['error_fallback'],
                'error': str(e)
            }

# Export the service
image_analysis_service = AdvancedImageAnalysisService()