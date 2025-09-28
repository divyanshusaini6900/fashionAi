#!/usr/bin/env python3
"""
Demo script for Gemini-based background prompt engineering.
This script demonstrates the new contextual background generation feature with sample data.
"""

import sys
import os
import asyncio
import logging
from pathlib import Path
import json

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

from app.services.image_generator import ImageGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def demo_contextual_backgrounds():
    """Demonstrate the contextual background generation feature."""
    logger.info("Demonstrating Gemini-based contextual background generation...")
    
    # Initialize the image generator
    image_generator = ImageGenerator()
    
    # Check if Gemini is available
    if not hasattr(image_generator, 'gemini_client'):
        logger.warning("Gemini client not available. Please check your configuration.")
        return False
    
    # Sample product data for testing - Wedding Gown
    wedding_gown_data = {
        "Description": "Elegant white wedding gown with lace details and long train",
        "Occasion": "wedding",
        "Gender": "women",
        "Key Features": [
            "Floor-length silhouette with mermaid fit",
            "Delicate lace bodice with pearl embellishments",
            "Off-shoulder neckline with delicate straps",
            "Long flowing train with lace overlay"
        ]
    }
    
    # Sample product data for testing - Casual T-Shirt
    casual_tshirt_data = {
        "Description": "Casual cotton t-shirt with colorful graphic print",
        "Occasion": "casual",
        "Gender": "unisex",
        "Key Features": [
            "100% premium cotton soft fabric",
            "Round neckline",
            "Vibrant graphic print on front",
            "Regular fit for everyday comfort"
        ]
    }
    
    # Sample product data for testing - Business Suit
    business_suit_data = {
        "Description": "Classic navy blue business suit with slim fit",
        "Occasion": "formal",
        "Gender": "men",
        "Key Features": [
            "Two-piece suit with blazer and trousers",
            "Classic notch lapel design",
            "Slim fit tailored silhouette",
            "Wrinkle-resistant wool blend fabric"
        ]
    }
    
    products = [
        ("Wedding Gown", wedding_gown_data),
        ("Casual T-Shirt", casual_tshirt_data),
        ("Business Suit", business_suit_data)
    ]
    
    try:
        for product_name, product_data in products:
            logger.info(f"\n--- Generating backgrounds for {product_name} ---")
            
            # Generate contextual backgrounds
            backgrounds = await image_generator._generate_contextual_backgrounds(product_data, count=3)
            
            logger.info(f"Generated backgrounds for {product_name}:")
            for i, bg in enumerate(backgrounds, 1):
                logger.info(f"  {i}. {bg}")
                
            # Show how these would be used in prompts
            logger.info(f"\nSample prompts that would be created for {product_name}:")
            for i, bg in enumerate(backgrounds[:2], 1):  # Show first 2
                sample_prompt = image_generator._create_generation_prompt(
                    product_data, 
                    f"frontside view in a {bg}", 
                    "9:16", 
                    product_data.get("Gender", "women")
                )
                # Just show first 500 characters to keep output manageable
                logger.info(f"  Prompt {i}: {sample_prompt[:500]}...")
        
        logger.info("\n" + "="*60)
        logger.info("DEMO COMPLETED SUCCESSFULLY!")
        logger.info("The system can now generate contextually appropriate backgrounds")
        logger.info("that match the product type, occasion, and style.")
        logger.info("="*60)
        return True
        
    except Exception as e:
        logger.error(f"Error during demo: {e}", exc_info=True)
        return False

def main():
    """Main demo function."""
    logger.info("Starting Gemini contextual background prompt engineering demo...")
    
    # Run the demo
    success = asyncio.run(demo_contextual_backgrounds())
    
    if success:
        logger.info("Demo completed successfully!")
        return 0
    else:
        logger.error("Demo failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())