"""
Test script for pose generation feature
"""
import asyncio
import logging
from app.services.image_generator import ImageGenerator
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_pose_generation():
    """Test the pose generation feature"""
    # Create an image generator instance
    image_generator = ImageGenerator()
    
    # Sample product data with pose recommendations
    product_data = {
        "Title": "Elegant Wedding Lehenga",
        "Description": "A beautiful wedding lehenga with intricate embroidery",
        "Occasion": "wedding",
        "Gender": "Women",
        "ModelPoses": [
            "Elegant standing pose with hands gently clasped, showcasing the full length of the lehenga",
            "Graceful three-quarter view pose with slight turn, highlighting the embroidery work",
            "Classic pose with one hand resting on hip, emphasizing the fitted blouse design"
        ]
    }
    
    # Test the prompt generation with pose information
    logger.info("Testing prompt generation with pose information...")
    
    try:
        # Generate a prompt with pose information
        prompt = image_generator._create_generation_prompt(
            product_data=product_data,
            background="grand wedding venue with decorative elements",
            aspect_ratio="9:16",
            gender="female"
        )
        
        logger.info(f"Generated prompt: {prompt}")
        
        # Check that the prompt contains pose information
        assert "Position model in a Elegant standing pose with hands gently clasped" in prompt
        logger.info("✓ Pose generation test passed")
        
        # Test with product data without pose information (fallback)
        product_data_no_pose = {
            "Title": "Casual Summer Dress",
            "Description": "A comfortable summer dress",
            "Occasion": "casual",
            "Gender": "Women"
        }
        
        prompt_no_pose = image_generator._create_generation_prompt(
            product_data=product_data_no_pose,
            background="peaceful garden setting with soft sunlight",
            aspect_ratio="9:16",
            gender="female"
        )
        
        logger.info(f"Generated prompt without pose info: {prompt_no_pose}")
        
        # Check that the prompt contains default pose information
        assert "Position model with confident, natural posture showcasing the outfit" in prompt_no_pose
        logger.info("✓ Fallback pose generation test passed")
        
    except Exception as e:
        logger.error(f"Error in pose generation test: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_pose_generation())