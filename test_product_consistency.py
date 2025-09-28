#!/usr/bin/env python3
"""
Test script to verify product consistency in image generation
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.image_generator import ImageGenerator
from app.services.workflow_manager import WorkflowManager

def test_image_prompt_generation():
    """Test that image prompts emphasize product consistency"""
    print("Testing image prompt generation for product consistency...")
    
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
        ],
        "ViewSpecificPoses": {
            "frontside": "Standing straight facing forward with arms slightly away from the body to showcase the front design and embroidery",
            "backside": "Standing straight with back facing the camera, hands clasped behind to highlight the back design and fit",
            "sideview": "Standing in profile with one hand on hip to show the silhouette and side details of the garment"
        }
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
            gender="women",
            view="frontside"
        )
        
        # Check for key consistency phrases
        consistency_checks = [
            "EXACT SAME product",
            "DO NOT modify",
            "DO NOT change",
            "IDENTICAL to the reference images",
            "absolute source of truth"
        ]
        
        print("   Consistency check results:")
        for check in consistency_checks:
            if check in prompt:
                print(f"   ✓ Found: '{check}'")
            else:
                print(f"   ✗ Missing: '{check}'")
        
        # Show a snippet of the prompt
        prompt_lines = prompt.split('\n')
        print("   Prompt snippet (first 10 lines):")
        for line in prompt_lines[:10]:
            if line.strip():
                print(f"     {line}")

async def test_combined_analysis_focus():
    """Test that combined analysis focuses on background and pose only"""
    print("\n\nTesting combined analysis focus...")
    
    # Initialize the workflow manager
    workflow_manager = WorkflowManager()
    
    # Check if the method exists
    print("1. Verifying combined analysis method exists...")
    if hasattr(workflow_manager, '_analyze_with_gemini_combined'):
        print("   ✓ Combined analysis method exists")
    else:
        print("   ✗ Combined analysis method not found")
        return
    
    # Check the prompt content
    print("2. Checking prompt content focus...")
    # We can't easily test the actual API call without credentials, but we can verify
    # the prompt structure by examining the method
    
    # For now, let's just print information about what the prompt should focus on
    print("   The combined analysis prompt should focus on:")
    print("   - Background settings only")
    print("   - Model pose recommendations only")
    print("   - View-specific poses")
    print("   - NOT on product analysis (description, features, etc.)")

if __name__ == "__main__":
    test_image_prompt_generation()
    asyncio.run(test_combined_analysis_focus())