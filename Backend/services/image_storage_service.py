import os
import uuid
import shutil
from pathlib import Path
import base64
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

class ImageStorageService:
    def __init__(self):
        # Create static images directory
        self.base_dir = Path(__file__).parent.parent
        self.images_dir = self.base_dir / "static" / "images" / "wardrobe"
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # Base URL for serving images
        self.base_url = "/static/images/wardrobe"
        
        logger.info(f"Image storage initialized: {self.images_dir}")
        
    def save_image(self, image_data, filename_prefix="item"):
        """
        Save image data and return the accessible URL
        """
        try:
            logger.info(f"Saving image with prefix: {filename_prefix}")
            
            # Validate input
            if image_data is None:
                logger.error("Image data is None")
                return None
                
            # Generate unique filename
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{filename_prefix}_{unique_id}.jpg"
            file_path = self.images_dir / filename
            
            logger.info(f"Generated filename: {filename}")
            logger.info(f"Full path: {file_path}")
            
            # Handle different types of image data
            if isinstance(image_data, str):
                if image_data.startswith('data:image/'):
                    # Base64 data URL
                    if ',' in image_data:
                        image_data = image_data.split(',')[1]
                    
                    # Decode base64
                    image_bytes = base64.b64decode(image_data)
                    logger.info(f"Decoded base64 data URL to {len(image_bytes)} bytes")
                    
                elif image_data.startswith('/9j/'):
                    # Direct base64 (JPEG starts with /9j/)
                    image_bytes = base64.b64decode(image_data)
                    logger.info(f"Decoded direct base64 to {len(image_bytes)} bytes")
                    
                elif image_data.startswith('file://') or os.path.exists(image_data):
                    # File path - copy the file
                    source_path = image_data.replace('file://', '') if image_data.startswith('file://') else image_data
                    if os.path.exists(source_path):
                        shutil.copy2(source_path, file_path)
                        url = f"{self.base_url}/{filename}"
                        logger.info(f"Copied file to {file_path}, URL: {url}")
                        return url
                    else:
                        logger.warning(f"Source image file not found: {source_path}")
                        return None
                else:
                    logger.error(f"Unsupported string format: {image_data[:50]}...")
                    return None
            else:
                # Assume it's binary data
                image_bytes = image_data
                logger.info(f"Using binary data: {len(image_bytes)} bytes")
            
            # Save the image if we have bytes
            if 'image_bytes' in locals() and image_bytes:
                # Optimize and save as JPEG
                image = Image.open(io.BytesIO(image_bytes))
                
                # Convert to RGB if necessary (for PNG with transparency)
                if image.mode in ('RGBA', 'LA', 'P'):
                    image = image.convert('RGB')
                
                # Resize if too large (max 800px width)
                if image.width > 800:
                    ratio = 800 / image.width
                    new_height = int(image.height * ratio)
                    image = image.resize((800, new_height), Image.Resampling.LANCZOS)
                
                # Save as JPEG with good quality
                image.save(file_path, 'JPEG', quality=85, optimize=True)
                
                url = f"{self.base_url}/{filename}"
                logger.info(f"Image saved successfully to {file_path}, URL: {url}")
                return url
            
            logger.error("No valid image data provided")
            return None
            
        except Exception as e:
            logger.error(f"Error saving image: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def delete_image(self, image_url):
        """Delete an image file"""
        try:
            if image_url and image_url.startswith(self.base_url):
                filename = image_url.split('/')[-1]
                file_path = self.images_dir / filename
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"Deleted image: {filename}")
        except Exception as e:
            logger.error(f"Error deleting image: {str(e)}")

# Global instance
image_storage_service = ImageStorageService()