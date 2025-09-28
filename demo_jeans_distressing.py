#!/usr/bin/env python3
"""
Demo script showcasing prompt engineering for jeans with distressing details
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.image_generator import ImageGenerator

def demo_jeans_distressing():
    """Demo the jeans distressing prompt engineering feature"""
    print("=== Jeans Distressing Prompt Engineering Demo ===\n")
    
    # Create a mock product data dictionary for jeans with distressing
    jeans_product_data = {
        "Description": "Ultra-distressed skinny jeans with multiple rips and fading",
        "Occasion": "casual",
        "Gender": "women",
        "Key Features": [
            "Skinny fit through hips and thighs",
            "Ultra-distressed with knee rips and thigh tears",
            "Authentic fading and whiskering details",
            "Destroyed pocket with intentional wear",
            "Stretch denim for comfort fit",
            "Button closure and zip fly",
            "Five-pocket styling with signature rivets"
        ],
        "RecommendedPoses": [
            "standing straight with hands on hips, showcasing the full length and distressing of the jeans",
            "sitting casually on a chair with one leg crossed, highlighting the knee distressing details",
            "walking naturally with confident stride to show the movement and fit of the jeans"
        ],
        "ViewSpecificPoses": {
            "frontside": "Standing straight facing forward to showcase the front distressing pattern and fit through hips and thighs",
            "backside": "Standing straight with back facing the camera to show the back pocket design, seat fit, and rear distressing",
            "sideview": "Standing in profile to show the leg silhouette, side distressing details, and overall tapered fit"
        }
    }
    
    # Initialize the image generator
    generator = ImageGenerator()
    
    # Sample backgrounds for jeans
    backgrounds = [
        "urban street with brick wall backdrop and concrete ground",
        "modern studio with softbox lighting and dark grey backdrop",
        "casual cafe setting with wooden tables and natural window light",
        "industrial loft with exposed pipes and metal framework",
        "skate park with concrete ledges and graffiti wall"
    ]
    
    print("Product: Ultra-distressed Skinny Jeans")
    print("Key Features:")
    for feature in jeans_product_data["Key Features"]:
        print(f"  - {feature}")
    
    print("\nGenerated Prompts for Different Backgrounds:")
    print("=" * 50)
    
    for i, background in enumerate(backgrounds, 1):
        print(f"\n{i}. Background: {background}")
        
        # Generate the prompt for jeans
        prompt = generator._create_generation_prompt(
            product_data=jeans_product_data,
            background=background,
            aspect_ratio="9:16",
            gender="women",
            view="frontside"
        )
        
        # Extract and show key sections of the prompt
        lines = prompt.split('\n')
        
        # Find the critical restrictions section
        distressing_section_start = -1
        for idx, line in enumerate(lines):
            if "CRITICAL RESTRICTIONS FOR JEANS WITH DISTRESSING" in line:
                distressing_section_start = idx
                break
        
        if distressing_section_start != -1:
            print("   Specialized Distressing Instructions:")
            for j in range(distressing_section_start + 1, min(distressing_section_start + 6, len(lines))):
                if lines[j].strip() and not lines[j].strip().startswith("-" * 50):
                    print(f"   {lines[j]}")
        else:
            print("   Standard Instructions (no specialized distressing section found)")
    
    print("\n" + "=" * 50)
    print("Benefits of Specialized Jeans Distressing Prompt Engineering:")
    print("1. Preserves exact distressing patterns and locations")
    print("2. Maintains authentic wash types and fading effects")
    print("3. Ensures hardware details (buttons, rivets, zippers) remain consistent")
    print("4. Keeps stitching patterns and thread colors accurate")
    print("5. Prevents AI from reinterpretating or redesigning distressing")
    print("6. Maintains brand consistency for denim products")
    
    print("\nThis specialized prompt engineering ensures that AI-generated images")
    print("of distressed jeans maintain the exact visual characteristics of the")
    print("reference images, including all intentional wear patterns and design details.")

if __name__ == "__main__":
    demo_jeans_distressing()