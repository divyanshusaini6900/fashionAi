#!/usr/bin/env python3
"""
Demo script showcasing aspect ratio prompt engineering
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.image_generator import ImageGenerator

def demo_aspect_ratio():
    """Demo the aspect ratio prompt engineering feature"""
    print("=== Aspect Ratio Prompt Engineering Demo ===\n")
    
    # Create a mock product data dictionary
    product_data = {
        "Description": "Designer summer dress with floral print",
        "Occasion": "casual",
        "Gender": "women",
        "Key Features": [
            "Lightweight fabric perfect for summer",
            "Floral print with vibrant colors",
            "Flowing A-line silhouette",
            "Adjustable spaghetti straps",
            "V-neck design with subtle pleating",
            "Knee-length hem with gentle flare"
        ],
        "RecommendedPoses": [
            "standing straight with hands gently clasped, showcasing the full length and flow of the dress",
            "sitting gracefully on a chair with one leg crossed, allowing the fabric to drape elegantly",
            "walking naturally with confident stride to show the movement and flare of the dress"
        ],
        "ViewSpecificPoses": {
            "frontside": "Standing straight facing forward to showcase the front design, V-neck, and floral pattern",
            "backside": "Standing straight with back facing the camera to show the back design and strap details",
            "sideview": "Standing in profile to show the A-line silhouette and gentle flare of the dress"
        }
    }
    
    # Initialize the image generator
    generator = ImageGenerator()
    
    # Define different aspect ratios with their use cases
    aspect_ratios = {
        "1:1": "Social media posts (Instagram, Facebook) - Perfect square format",
        "16:9": "Website banners, digital displays - Widescreen format",
        "4:3": "Standard photo prints, presentations - Traditional format",
        "3:4": "Portrait photography, mobile viewing - Vertical format",
        "9:16": "Mobile social media (Instagram Stories, TikTok) - Portrait format"
    }
    
    background = "sunny garden with blooming flowers and soft natural lighting"
    
    print("Product: Designer Summer Dress with Floral Print")
    print("Key Features:")
    for feature in product_data["Key Features"]:
        print(f"  - {feature}")
    
    print("\nGenerated Prompts for Different Aspect Ratios:")
    print("=" * 60)
    
    for aspect_ratio, use_case in aspect_ratios.items():
        print(f"\nAspect Ratio: {aspect_ratio}")
        print(f"Use Case: {use_case}")
        
        # Generate the prompt
        prompt = generator._create_generation_prompt(
            product_data=product_data,
            background=background,
            aspect_ratio=aspect_ratio,
            gender="women",
            view="frontside"
        )
        
        # Extract and show the aspect ratio enforcement section
        lines = prompt.split('\n')
        
        # Find the aspect ratio enforcement section
        enforcement_section_start = -1
        for idx, line in enumerate(lines):
            if "ASPECT RATIO ENFORCEMENT" in line:
                enforcement_section_start = idx
                break
        
        if enforcement_section_start != -1:
            print("   Aspect Ratio Enforcement Instructions:")
            for j in range(enforcement_section_start, min(enforcement_section_start + 5, len(lines))):
                if lines[j].strip() and not lines[j].strip().startswith("-" * 50):
                    print(f"   {lines[j]}")
        else:
            print("   Standard Instructions (no aspect ratio enforcement section found)")
    
    print("\n" + "=" * 60)
    print("Benefits of Explicit Aspect Ratio Prompt Engineering:")
    print("1. Ensures generated images match the exact dimensions requested")
    print("2. Prevents cropping, stretching, or distortion of images")
    print("3. Maintains consistent composition across all aspect ratios")
    print("4. Preserves all visual elements and proportions as specified")
    print("5. Provides clear instructions for AI models to follow")
    print("6. Eliminates ambiguity in image generation requests")
    
    print("\nThis specialized prompt engineering ensures that AI-generated images")
    print("maintain the exact aspect ratio specified in the request, preventing")
    print("any unwanted cropping, stretching, or distortion that could affect")
    print("the final visual quality and composition of the fashion images.")

if __name__ == "__main__":
    demo_aspect_ratio()