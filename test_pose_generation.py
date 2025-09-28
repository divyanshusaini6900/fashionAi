#!/usr/bin/env python3
"""
Test script to verify pose generation functionality
"""

import asyncio
import sys
import os
import random

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.image_generator import ImageGenerator

def test_pose_selection():
    """Test the pose selection functionality"""
    print("Testing pose selection functionality...")
    
    # Create a mock product data dictionary with pose recommendations
    product_data_with_poses = {
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
    
    # Create a mock product data dictionary without pose recommendations
    product_data_without_poses = {
        "Description": "Casual summer dress with floral pattern",
        "Occasion": "casual",
        "Gender": "women",
        "Key Features": ["lightweight fabric", "flowing skirt", "v-neck"]
    }
    
    # Initialize the image generator
    generator = ImageGenerator()
    
    # Test pose selection with recommendations
    print("\n1. Testing pose selection with recommendations...")
    poses_selected = []
    for i in range(5):  # Test multiple times to see randomness
        # Mock the _create_generation_prompt method to just return the pose
        background = "elegant ballroom with chandeliers"
        aspect_ratio = "9:16"
        gender = "women"
        
        # Get pose recommendation if available
        pose_recommendations = product_data_with_poses.get('RecommendedPoses', [])
        if pose_recommendations:
            # Randomly select one of the recommended poses for variety
            pose = random.choice(pose_recommendations)
        else:
            pose = "standing straight with confident, natural posture showcasing the outfit"
        
        poses_selected.append(pose)
        print(f"  Selected pose {i+1}: {pose}")
    
    # Check if different poses were selected (indicating randomness is working)
    unique_poses = set(poses_selected)
    print(f"  Unique poses selected: {len(unique_poses)} out of {len(poses_selected)} trials")
    
    # Test pose selection without recommendations
    print("\n2. Testing pose selection without recommendations...")
    background = "casual cafe setting"
    aspect_ratio = "9:16"
    gender = "women"
    
    # Get pose recommendation if available
    pose_recommendations = product_data_without_poses.get('RecommendedPoses', [])
    if pose_recommendations:
        # Randomly select one of the recommended poses for variety
        pose = random.choice(pose_recommendations)
    else:
        pose = "standing straight with confident, natural posture showcasing the outfit"
    
    print(f"  Default pose selected: {pose}")

if __name__ == "__main__":
    test_pose_selection()