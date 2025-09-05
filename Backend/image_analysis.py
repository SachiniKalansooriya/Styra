# Backend/image_analysis.py - AI-powered version with fallback
from services.free_ai_analyzer import free_ai_analyzer
import logging

logger = logging.getLogger(__name__)

# Try to import simple_analyzer as fallback, but continue if not available
try:
    from services.simple_analyzer import simple_analyzer
    HAS_FALLBACK = True
except ImportError:
    logger.warning("Simple analyzer not available, running without fallback")
    simple_analyzer = None
    HAS_FALLBACK = False

class AdvancedImageAnalysisService:
    """Image analysis service with AI and fallback capabilities"""
    
    def __init__(self):
        # Try to use free AI analyzer first, fallback to simple analyzer if available
        try:
            self.primary_analyzer = free_ai_analyzer
            self.fallback_analyzer = simple_analyzer if HAS_FALLBACK else None
            
            if self.fallback_analyzer:
                logger.info("Image analysis service initialized (AI mode with fallback)")
            else:
                logger.info("Image analysis service initialized (AI mode without fallback)")
        except Exception as e:
            logger.warning(f"Could not initialize AI analyzer: {e}")
            if HAS_FALLBACK:
                self.primary_analyzer = simple_analyzer
                self.fallback_analyzer = None
                logger.info("Image analysis service initialized (simple mode only)")
            else:
                # Create a minimal analyzer if nothing else is available
                self.primary_analyzer = self._create_minimal_analyzer()
                self.fallback_analyzer = None
                logger.warning("Image analysis service initialized (minimal mode - limited functionality)")
    
    def _create_minimal_analyzer(self):
        """Create a minimal analyzer when no other analyzers are available"""
        class MinimalAnalyzer:
            def analyze_clothing_item(self, image_data):
                return {
                    'suggestedCategory': 'tops',
                    'suggestedColor': 'Unknown',
                    'suggestedOccasion': 'casual',
                    'confidence': 0.3,
                    'analysis_method': 'minimal_fallback',
                    'success': True
                }
            
            def get_service_status(self):
                return {
                    'ai_models_loaded': False,
                    'supported_categories': ['tops', 'bottoms', 'dresses', 'accessories'],
                    'supported_colors': ['Unknown'],
                    'analysis_methods': ['minimal_fallback']
                }
        
        return MinimalAnalyzer()
    
    def analyze_clothing_item(self, image_data: bytes):
        """Main analysis method with AI and fallback"""
        try:
            # Try primary analyzer (AI if available)
            result = self.primary_analyzer.analyze_clothing_item(image_data)
            
            # If AI analysis has low confidence and fallback is available, try fallback
            if (result.get('confidence', 0) < 0.5 and 
                self.fallback_analyzer is not None):
                
                logger.info("AI confidence low, trying fallback analyzer...")
                fallback_result = self.fallback_analyzer.analyze_clothing_item(image_data)
                
                # Use fallback if it has better confidence
                if fallback_result.get('confidence', 0) > result.get('confidence', 0):
                    fallback_result['analysis_method'] = f"{result.get('analysis_method', 'ai')}_with_fallback"
                    result = fallback_result
            
            logger.info(f"Analysis completed: {result.get('analysis_method', 'unknown')} - confidence: {result.get('confidence', 0):.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Analysis service error: {e}")
            # Try fallback analyzer if primary fails and fallback is available
            if self.fallback_analyzer is not None:
                try:
                    logger.info("Primary analyzer failed, trying fallback...")
                    result = self.fallback_analyzer.analyze_clothing_item(image_data)
                    result['analysis_method'] = 'fallback_after_error'
                    return result
                except Exception as fallback_error:
                    logger.error(f"Fallback analyzer also failed: {fallback_error}")
            
            # Return basic error response
            return {
                'suggestedCategory': 'tops',
                'suggestedColor': 'Unknown',
                'suggestedOccasion': 'casual',
                'confidence': 0.3,
                'analysis_method': 'service_error',
                'error': str(e)
            }
    
    def get_service_info(self):
        """Get service information"""
        try:
            primary_status = self.primary_analyzer.get_service_status()
            
            # Add information about fallback availability
            if self.fallback_analyzer is not None:
                fallback_status = self.fallback_analyzer.get_service_status()
                primary_status['fallback_available'] = True
                primary_status['fallback_methods'] = fallback_status.get('analysis_methods', [])
            else:
                primary_status['fallback_available'] = False
            
            return primary_status
            
        except Exception as e:
            logger.error(f"Error getting service info: {e}")
            return {
                'ai_models_loaded': False,
                'supported_categories': ['tops', 'bottoms', 'dresses', 'shoes', 'accessories', 'outerwear'],
                'supported_colors': ['Unknown'],
                'analysis_methods': ['error_fallback'],
                'error': str(e)
            }

# Create global instance
image_analysis_service = AdvancedImageAnalysisService()