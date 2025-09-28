#!/usr/bin/env python3
"""
Test script to verify Gemini background generation functionality
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.image_generator import ImageGenerator

async def test_background_generation():
    """Test the background generation functionality"""
    print("Testing Gemini background generation...")
    
    # Create a mock product data dictionary
    product_data = {
        "Description": "Elegant evening gown with floral embroidery",
        "Occasion": "wedding",
        "Gender": "women",
        "Key Features": ["floral embroidery", "flowing silhouette", "delicate lace"]
    }
    
    # Initialize the image generator
    generator = ImageGenerator()
    
    # Test contextual background generation
    print("\n1. Testing contextual background generation...")
    try:
        backgrounds = await generator._generate_contextual_backgrounds(product_data, count=3)
        print(f"Generated {len(backgrounds)} backgrounds:")
        for i, bg in enumerate(backgrounds, 1):
            print(f"  {i}. {bg}")
    except Exception as e:
        print(f"Error generating contextual backgrounds: {e}")
    
    # Test dynamic background generation (fallback)
    print("\n2. Testing dynamic background generation (fallback)...")
    try:
        backgrounds = generator._generate_dynamic_backgrounds("wedding", count=3)
        print(f"Generated {len(backgrounds)} dynamic backgrounds:")
        for i, bg in enumerate(backgrounds, 1):
            print(f"  {i}. {bg}")
    except Exception as e:
        print(f"Error generating dynamic backgrounds: {e}")
    
    # Test fallback background variations
    print("\n3. Testing fallback background variations...")
    try:
        backgrounds = generator._get_background_variations("wedding")
        print(f"Generated {len(backgrounds)} fallback backgrounds:")
        for i, bg in enumerate(backgrounds, 1):
            print(f"  {i}. {bg}")
    except Exception as e:
        print(f"Error generating fallback backgrounds: {e}")

if __name__ == "__main__":
    asyncio.run(test_background_generation())
