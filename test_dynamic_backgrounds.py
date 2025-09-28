"""
Test script for dynamic background generation with Gemini
"""
import asyncio
import logging
from app.services.image_generator import ImageGenerator
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_dynamic_backgrounds():
    """Test the dynamic background generation feature"""
    # Create an image generator instance
    image_generator = ImageGenerator()
    
    # Sample product data with occasion
    product_data = {
        "Title": "Elegant Wedding Lehenga",
        "Description": "A beautiful wedding lehenga with intricate embroidery",
        "Occasion": "wedding",
        "Ideal For": "Women"
    }
    
    # Test the dynamic background generation
    logger.info("Testing dynamic background generation...")
    
    try:
        backgrounds = await image_generator._get_background_variations("wedding", product_data)
        logger.info(f"Generated backgrounds: {backgrounds}")
        
        # Check that we got the expected number of backgrounds
        assert len(backgrounds) >= 1, "Should have at least one background"
        logger.info("✓ Background generation test passed")
        
        # Test with a different occasion
        casual_backgrounds = await image_generator._get_background_variations("casual", product_data)
        logger.info(f"Generated casual backgrounds: {casual_backgrounds}")
        assert len(casual_backgrounds) >= 1, "Should have at least one background"
        logger.info("✓ Casual background generation test passed")
        
    except Exception as e:
        logger.error(f"Error in background generation test: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_dynamic_backgrounds())