"""
Test script for jeans distressing details feature
"""
import asyncio
import logging
from app.services.image_generator import ImageGenerator
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_jeans_distressing():
    """Test the jeans distressing details feature"""
    # Create an image generator instance
    image_generator = ImageGenerator()
    
    # Sample product data for jeans with distressing details
    product_data_jeans = {
        "Title": "Ripped Skinny Jeans",
        "Description": "Trendy ripped jeans with fashionable distressing details",
        "Occasion": "casual",
        "Gender": "Men",
        "DistressingDetails": [
            {
                "location": "left knee",
                "type": "ripped",
                "severity": "medium",
                "description": "Torn fabric with visible fraying edges"
            },
            {
                "location": "right thigh",
                "type": "faded",
                "severity": "light",
                "description": "Subtle fading for a worn-in look"
            },
            {
                "location": "left pocket area",
                "type": "worn",
                "severity": "medium",
                "description": "Distressed pocket corners with slight fabric wear"
            }
        ]
    }
    
    # Test the prompt generation with distressing information
    logger.info("Testing prompt generation with jeans distressing details...")
    
    try:
        # Generate a prompt with distressing details
        prompt = image_generator._create_generation_prompt(
            product_data=product_data_jeans,
            background="urban street setting with brick wall",
            aspect_ratio="9:16",
            gender="male"
        )
        
        logger.info(f"Generated prompt: {prompt}")
        
        # Check that the prompt contains distressing information
        assert "DISTRESSING DETAILS" in prompt
        assert "left knee: ripped (medium severity)" in prompt
        assert "right thigh: faded (light severity)" in prompt
        assert "left pocket area: worn (medium severity)" in prompt
        logger.info("✓ Jeans distressing details test passed")
        
        # Test with product data without distressing information (regular product)
        product_data_regular = {
            "Title": "Casual Summer Dress",
            "Description": "A comfortable summer dress",
            "Occasion": "casual",
            "Gender": "Women"
        }
        
        prompt_regular = image_generator._create_generation_prompt(
            product_data=product_data_regular,
            background="peaceful garden setting with soft sunlight",
            aspect_ratio="9:16",
            gender="female"
        )
        
        logger.info(f"Generated prompt for regular product: {prompt_regular}")
        
        # Check that the prompt does not contain distressing information
        assert "DISTRESSING DETAILS" not in prompt_regular
        logger.info("✓ Regular product (no distressing) test passed")
        
    except Exception as e:
        logger.error(f"Error in jeans distressing test: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_jeans_distressing())