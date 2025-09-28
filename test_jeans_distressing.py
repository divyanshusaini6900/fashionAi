#!/usr/bin/env python3
"""
Test script to verify jeans distressing prompt engineering
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.image_generator import ImageGenerator

def test_jeans_distressing_prompt():
    """Test that image prompts for jeans with distressing are properly generated"""
    print("Testing jeans distressing prompt generation...")
    
    # Create a mock product data dictionary for jeans with distressing
    jeans_product_data = {
        "Description": "Distressed skinny jeans with ripped knees and fading",
        "Occasion": "casual",
        "Gender": "women",
        "Key Features": ["skinny fit", "distressed knees", "fading effect", "ripped details", "stretch denim"],
        "RecommendedPoses": [
            "standing straight with hands on hips, showcasing the full length of the jeans",
            "sitting casually with one leg crossed, highlighting the knee distressing",
            "walking naturally to show the movement and fit of the jeans"
        ],
        "ViewSpecificPoses": {
            "frontside": "Standing straight facing forward to showcase the front distressing and fit",
            "backside": "Standing straight with back facing the camera to show the back pocket design and seat fit",
            "sideview": "Standing in profile to show the leg silhouette and side distressing details"
        }
    }
    
    # Create a mock product data dictionary for regular product (not jeans)
    regular_product_data = {
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
    
    # Test backgrounds
    backgrounds = [
        "urban street with brick wall backdrop",
        "modern studio with soft lighting",
        "casual cafe setting with natural light"
    ]
    
    print("\n1. Testing jeans distressing prompt generation...")
    for i, background in enumerate(backgrounds, 1):
        print(f"\n   Background {i}: {background}")
        
        # Generate the prompt for jeans
        prompt = generator._create_generation_prompt(
            product_data=jeans_product_data,
            background=background,
            aspect_ratio="9:16",
            gender="women",
            view="frontside"
        )
        
        # Check for jeans-specific keywords
        jeans_checks = [
            "distressing details",
            "rips, tears, fading",
            "knee tears, thigh rips",
            "wash pattern",
            "DO NOT change the location, size, or shape of any rips or tears"
        ]
        
        print("   Jeans-specific checks:")
        for check in jeans_checks:
            if check in prompt:
                print(f"   ✓ Found: '{check}'")
            else:
                print(f"   ✗ Missing: '{check}'")
        
        # Show a snippet of the prompt
        prompt_lines = prompt.split('\n')
        print("   Prompt snippet (first 5 lines):")
        for line in prompt_lines[:5]:
            if line.strip():
                print(f"     {line}")
    
    print("\n2. Testing regular product prompt generation (should not have jeans-specific content)...")
    for i, background in enumerate(backgrounds, 1):
        print(f"\n   Background {i}: {background}")
        
        # Generate the prompt for regular product
        prompt = generator._create_generation_prompt(
            product_data=regular_product_data,
            background=background,
            aspect_ratio="9:16",
            gender="women",
            view="frontside"
        )
        
        # Check that jeans-specific keywords are NOT present
        jeans_checks = [
            "distressing details",
            "rips, tears, fading",
            "knee tears, thigh rips",
            "wash pattern"
        ]
        
        print("   Ensuring jeans-specific content is NOT present:")
        for check in jeans_checks:
            if check in prompt:
                print(f"   ✗ Unexpectedly found: '{check}'")
            else:
                print(f"   ✓ Correctly absent: '{check}'")
        
        # Show a snippet of the prompt
        prompt_lines = prompt.split('\n')
        print("   Prompt snippet (first 5 lines):")
        for line in prompt_lines[:5]:
            if line.strip():
                print(f"     {line}")

if __name__ == "__main__":
    test_jeans_distressing_prompt()