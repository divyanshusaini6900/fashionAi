#!/usr/bin/env python3
"""
Test script to verify the full pose generation workflow
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.image_generator import ImageGenerator

async def test_full_prompt_generation():
    """Test the full prompt generation with poses"""
    print("Testing full prompt generation with pose functionality...")
    
    # Create a mock product data dictionary with pose recommendations
    product_data = {
        "Description": "Elegant evening gown with floral embroidery",
        "Occasion": "wedding",
        "Gender": "women",
        "Key Features": ["floral embroidery", "flowing silhouette", "delicate lace"],
        "RecommendedPoses": [
            "standing straight with hands gently clasped in front, showcasing the full length and embroidery of the gown",
            "sitting gracefully on a chair with one leg crossed, allowing the fabric to drape elegantly",
            "twirling slightly to show the flow and movement of the gown fabric"
        ]
    }
    
    # Initialize the image generator
    generator = ImageGenerator()
    
    # Test prompt generation with different backgrounds
    backgrounds = [
        "elegant ballroom with chandeliers",
        "romantically lit conservatory at twilight",
        "sun-drenched balcony of a luxurious Mediterranean villa"
    ]
    
    print("\nGenerating prompts with different backgrounds and poses...")
    for i, background in enumerate(backgrounds, 1):
        print(f"\n{i}. Background: {background}")
        
        # Generate the prompt
        prompt = generator._create_generation_prompt(
            product_data=product_data,
            background=background,
            aspect_ratio="9:16",
            gender="women"
        )
        
        # Extract and show the pose part of the prompt
        lines = prompt.split('\n')
        pose_line = None
        for line in lines:
            if 'Position model' in line or 'Position model' in line:
                pose_line = line.strip()
                break
        
        if pose_line:
            print(f"   Pose instruction: {pose_line}")
        else:
            print("   Pose instruction not found in prompt")
        
        # Show a snippet of the prompt
        prompt_lines = prompt.split('\n')
        for line in prompt_lines[:5]:  # Show first 5 lines
            if line.strip():
                print(f"   Prompt snippet: {line}")
                break

if __name__ == "__main__":
    asyncio.run(test_full_prompt_generation())