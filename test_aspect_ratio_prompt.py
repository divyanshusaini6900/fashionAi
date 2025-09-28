#!/usr/bin/env python3
"""
Test script to verify aspect ratio prompt engineering
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.image_generator import ImageGenerator

def test_aspect_ratio_prompt():
    """Test that image prompts include explicit aspect ratio instructions"""
    print("Testing aspect ratio prompt engineering...")
    
    # Create a mock product data dictionary
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
    
    # Test different aspect ratios
    aspect_ratios = ["1:1", "16:9", "4:3", "3:4", "9:16"]
    background = "elegant ballroom with chandeliers"
    
    print("\nTesting different aspect ratios:")
    print("=" * 50)
    
    for aspect_ratio in aspect_ratios:
        print(f"\nAspect Ratio: {aspect_ratio}")
        
        # Generate the prompt
        prompt = generator._create_generation_prompt(
            product_data=product_data,
            background=background,
            aspect_ratio=aspect_ratio,
            gender="women",
            view="frontside"
        )
        
        # Check for aspect ratio enforcement keywords
        aspect_checks = [
            "ASPECT RATIO ENFORCEMENT",
            f"EXACTLY {aspect_ratio}",
            "CRITICALLY IMPORTANT",
            "DO NOT crop, stretch, or distort"
        ]
        
        print("   Aspect ratio enforcement checks:")
        for check in aspect_checks:
            if check in prompt:
                print(f"   ✓ Found: '{check}'")
            else:
                print(f"   ✗ Missing: '{check}'")
        
        # Show a snippet of the prompt
        prompt_lines = prompt.split('\n')
        print("   Prompt snippet (first 3 lines):")
        for line in prompt_lines[:3]:
            if line.strip():
                print(f"     {line}")
    
    # Test with jeans product to ensure both aspect ratio and distressing instructions are present
    print("\n" + "=" * 50)
    print("Testing jeans product with distressing:")
    
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
    
    prompt = generator._create_generation_prompt(
        product_data=jeans_product_data,
        background=background,
        aspect_ratio="16:9",
        gender="women",
        view="frontside"
    )
    
    # Check for both aspect ratio and distressing keywords
    combined_checks = [
        "ASPECT RATIO ENFORCEMENT",
        "CRITICAL RESTRICTIONS FOR JEANS WITH DISTRESSING",
        "EXACTLY 16:9",
        "distressing pattern",
        "DO NOT reinterpret or redesign"
    ]
    
    print("   Combined checks for jeans with aspect ratio:")
    for check in combined_checks:
        if check in prompt:
            print(f"   ✓ Found: '{check}'")
        else:
            print(f"   ✗ Missing: '{check}'")

if __name__ == "__main__":
    test_aspect_ratio_prompt()