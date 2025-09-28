#!/usr/bin/env python3
"""
Test script to verify background generation integration with concurrent image generator
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.concurrent_image_generator import ConcurrentImageGenerator

async def test_concurrent_background_generation():
    """Test the concurrent background generation functionality"""
    print("Testing concurrent background generation integration...")
    
    # Create a mock product data dictionary
    product_data = {
        "Description": "Stylish summer dress with floral pattern",
        "Occasion": "casual",
        "Gender": "women",
        "Key Features": ["lightweight fabric", "flowing skirt", "v-neck"]
    }
    
    # Initialize the concurrent image generator
    async with ConcurrentImageGenerator() as generator:
        # Test dynamic background generation (fallback method)
        print("\n1. Testing dynamic background generation...")
        try:
            backgrounds = generator._generate_dynamic_backgrounds("casual", count=5)
            print(f"Generated {len(backgrounds)} dynamic backgrounds:")
            for i, bg in enumerate(backgrounds, 1):
                print(f"  {i}. {bg}")
        except Exception as e:
            print(f"Error generating dynamic backgrounds: {e}")
        
        # Test fallback background variations
        print("\n2. Testing fallback background variations...")
        try:
            backgrounds = generator._get_background_variations("casual")
            print(f"Generated {len(backgrounds)} fallback backgrounds:")
            for i, bg in enumerate(backgrounds, 1):
                print(f"  {i}. {bg}")
        except Exception as e:
            print(f"Error generating fallback backgrounds: {e}")

if __name__ == "__main__":
    asyncio.run(test_concurrent_background_generation())