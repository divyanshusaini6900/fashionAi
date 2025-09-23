#!/usr/bin/env python3
"""
Quick Test Script for Multi-Agent Product Listing System
Run this script to test the system with minimal setup
"""

import asyncio
import os
from pathlib import Path

# Add the main system import
from multiagent_system import MultiAgentProductSystem, InputHandler

async def quick_test():
    """Run a quick test with sample data"""
    print("🚀 Quick Test - Multi-Agent Product Listing System")
    print("=" * 50)
    
    # Check if API keys are set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Please set OPENAI_API_KEY environment variable")
        return
    
    if not os.getenv("REPLICATE_API_TOKEN"):
        print("❌ Please set REPLICATE_API_TOKEN environment variable") 
        return
    
    # Sample test data
    sample_text = """
    Black leather dress shoes for men
    Size 10.5 US
    Oxford style with laces
    Genuine leather upper
    Professional business wear
    Price around $120
    """
    
    # Look for test images
    test_image_paths = []
    for ext in ['jpg', 'jpeg', 'png']:
        test_image_paths.extend(Path("test_images").glob(f"**/*.{ext}"))
    
    # Convert to strings and limit to 4 images
    image_paths = [str(p) for p in test_image_paths[:4]]
    
    print(f"📊 Found {len(image_paths)} test images")
    print(f"📝 Using sample text: {sample_text.strip()[:50]}...")
    
    # Process images
    images = InputHandler.process_multiple_images(image_paths)
    
    # Initialize system
    system = MultiAgentProductSystem(
        shoe_excel_path="excel_files/shoes_data.xlsx",
        jewellery_excel_path="excel_files/jewellery_data.xlsx"
    )
    
    # Run the system
    try:
        result = await system.process_product_input(images, sample_text.strip())
        
        print("\n🎉 Test completed successfully!")
        print("📋 Results:")
        print(f"   Category: {result['category']}")
        print(f"   Target Demographic: {result['target_demographic']}")
        print(f"   Generated Images: {len(result['generated_images'])}")
        print(f"   Status: {result['status']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(quick_test())
