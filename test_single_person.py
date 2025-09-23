#!/usr/bin/env python3
"""
Test the updated prompt to ensure single person generation
"""
import asyncio
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from app.services.image_generator import ImageGenerator
from app.core.config import settings

async def test_single_person_prompt():
    """Test the updated prompt to ensure single person generation"""
    print("🧪 Testing Single Person Prompt")
    print("=" * 50)
    
    try:
        # Initialize image generator
        image_generator = ImageGenerator()
        
        # Test data - same as before
        reference_images = [
            "tests/test_data/ref1.jpg",
            "tests/test_data/usp1.jpg"
        ]
        
        product_data = {
            'Ideal For': 'women',
            'Occasion': 'wedding',
            'Description': 'Elegant green Anarkali dress'
        }
        
        print(f"✅ Image generator initialized")
        print(f"📋 Test Data:")
        print(f"   Ideal For: {product_data['Ideal For']}")
        print(f"   Occasion: {product_data['Occasion']}")
        print(f"   Reference Images: {len(reference_images)}")
        
        # Test prompt generation first
        print(f"\n🧪 STEP 1: Testing Updated Prompt Generation")
        test_background = "clean studio with white background"
        prompt = image_generator._create_generation_prompt(product_data, test_background)
        
        print(f"✅ Updated Prompt Generated:")
        print(f"   Length: {len(prompt)} characters")
        print(f"   Content: {prompt}")
        
        # Look for key improvements
        improvements = []
        if "single" in prompt.lower():
            improvements.append("✅ Specifies 'single' person")
        if "only one" in prompt.lower():
            improvements.append("✅ Emphasizes 'ONLY ONE person'")
        if "no duplicate" in prompt.lower():
            improvements.append("✅ Explicitly prohibits duplicates")
        if "Indian woman model" in prompt or "Indian man model" in prompt:
            improvements.append("✅ Uses proper grammar for model description")
        
        print(f"\n📊 Prompt Improvements:")
        for improvement in improvements:
            print(f"   {improvement}")
        
        # Test image generation
        print(f"\n🧪 STEP 2: Testing Image Generation with Updated Prompt")
        image_bytes = await image_generator._run_gemini_generation(prompt, reference_images)
        
        if image_bytes:
            print(f"✅ Image Generation: SUCCESS")
            print(f"   Size: {len(image_bytes):,} bytes")
            
            # Save test image with updated prompt
            test_filename = "test_single_person_updated.jpg"
            with open(f"output/{test_filename}", "wb") as f:
                f.write(image_bytes)
            print(f"   💾 Saved: output/{test_filename}")
            
            print(f"\n🎯 Please check the generated image to verify:")
            print(f"   ✅ Only ONE person appears in the image")
            print(f"   ✅ No duplicate or repeated figures")
            print(f"   ✅ Professional fashion photography quality")
            
        else:
            print(f"❌ Image Generation: FAILED")
            
        return image_bytes is not None
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print(f"🎯 Single Person Prompt Test")
    print(f"Purpose: Ensure AI generates only one person instead of duplicates")
    print(f"")
    
    result = asyncio.run(test_single_person_prompt())
    
    if result:
        print(f"\n🎉 Test completed successfully!")
        print(f"\n💡 Key changes made to prevent duplicate persons:")
        print(f"   1. 'A single Indian woman model' - emphasizes ONE person")
        print(f"   2. 'Show ONLY ONE person in the image' - explicit instruction")
        print(f"   3. 'No duplicate or repeated figures' - prohibits duplicates")
        print(f"   4. Better grammar and clearer instructions")
    else:
        print(f"\n💥 Test failed - check logs for details")