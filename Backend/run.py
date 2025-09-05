# Backend/run.py
import uvicorn
import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('styra_backend.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main function to run the Styra AI Backend"""
    try:
        # Get configuration from environment
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", 8000))
        debug_mode = os.getenv("DEBUG", "True").lower() == "true"
        
        logger.info("Starting Styra AI Wardrobe Backend...")
        logger.info(f"Host: {host}")
        logger.info(f"Port: {port}")
        logger.info(f"Debug Mode: {debug_mode}")
        
        # Check if required dependencies are available
        try:
            import torch
            import transformers
            logger.info("AI dependencies available - Free AI analysis enabled")
        except ImportError as e:
            logger.warning(f"AI dependencies missing: {e}")
            logger.info("Will use rule-based analysis as fallback")
        
        # Run the server
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=debug_mode,
            log_level="info" if debug_mode else "warning",
            access_log=True
        )
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()