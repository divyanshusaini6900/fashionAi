#!/usr/bin/env python3
"""
Debug the workflow to find where it's failing
"""
import asyncio
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent))

from app.core.config import settings
from app.services.image_generator import ImageGenerator
from tests.run_api_test import ensure_test_images

async def debug_image_workflow():
    """Debug each step of the image generation workflow"""
    print("🔍 DEBUGGING IMAGE GENERATION WORKFLOW")
    print("=" * 60)
    
    ensure_test_images()
    
    # Initialize image generator
    image_generator = ImageGenerator()
    print(f"✅ Image generator initialized")
    print(f"   USE_GEMINI_FOR_IMAGES: {settings.USE_GEMINI_FOR_IMAGES}")
    
    # Test data that matches what the API receives
    reference_image_paths_dict = {
        "frontside": "tests/test_data/ref1.jpg",
        "detailview": "tests/test_data/usp1.jpg"
    }
    
    product_data = {
        "Ideal For": "women",
        "Occasion": "wedding"
    }
    
    number_of_outputs = 2
    
    print(f"\n📋 Test Parameters:")
    print(f"   Reference Images: {list(reference_image_paths_dict.keys())}")
    print(f"   Product Data: {product_data}")
    print(f"   Number of Outputs: {number_of_outputs}")
    
    try:
        # Test Step 1: Direct Gemini generation (we know this works)
        print(f"\n🧪 STEP 1: Direct Gemini Generation")
        simple_prompt = "Indian woman model wearing elegant dress in studio"
        reference_images = list(reference_image_paths_dict.values())
        
        result1 = await image_generator._run_gemini_generation(simple_prompt, reference_images)
        if result1:
            print(f"✅ Direct Gemini: SUCCESS ({len(result1)} bytes)")
        else:
            print(f"❌ Direct Gemini: FAILED")
        
        # Test Step 2: _run_image_generation method (the wrapper)
        print(f"\n🧪 STEP 2: Image Generation Wrapper")
        result2 = await image_generator._run_image_generation(simple_prompt, reference_images)
        if result2:
            print(f"✅ Image Generation Wrapper: SUCCESS ({len(result2)} bytes)")
        else:
            print(f"❌ Image Generation Wrapper: FAILED")
        
        # Test Step 3: Full generate_images workflow
        print(f"\n🧪 STEP 3: Full Generate Images Workflow")
        try:
            primary_image, all_variations = await image_generator.generate_images(
                product_data=product_data,
                reference_image_paths_dict=reference_image_paths_dict,
                number_of_outputs=number_of_outputs
            )
            
            if primary_image:
                print(f"✅ Full Workflow: SUCCESS")
                print(f"   Primary Image: {len(primary_image)} bytes")
                print(f"   Variations: {len(all_variations)} images")
                print(f"   Variation Keys: {list(all_variations.keys())}")
            else:
                print(f"❌ Full Workflow: FAILED - No primary image")
                print(f"   Variations: {len(all_variations)} images")
                
        except Exception as e:
            print(f"❌ Full Workflow: EXCEPTION - {str(e)}")
            print(f"   Error Type: {type(e).__name__}")
        
        # Test Step 4: Check prompt creation
        print(f"\n🧪 STEP 4: Prompt Creation")
        try:
            prompt1 = image_generator._create_generation_prompt(product_data, "frontside view in a clean studio")
            print(f"✅ Prompt Creation: SUCCESS")
            print(f"   Prompt Length: {len(prompt1)} characters")
            print(f"   Prompt Preview: {prompt1[:100]}...")
        except Exception as e:
            print(f"❌ Prompt Creation: FAILED - {str(e)}")
        
        print(f"\n🎯 DIAGNOSIS:")
        print("=" * 60)
        
        if result1 and result2:
            print(f"✅ Gemini API is working correctly")
            print(f"⚠️ Issue is likely in the workflow logic or exception handling")
        elif result1 and not result2:
            print(f"✅ Gemini API works directly")
            print(f"❌ Issue is in the wrapper method (_run_image_generation)")
        elif not result1:
            print(f"❌ Gemini API is not working (quota/API issue)")
        
        return True
        
    except Exception as e:
        print(f"❌ DEBUG FAILED: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_image_workflow())
    print(f"\n{'🎉 DEBUG COMPLETED' if success else '❌ DEBUG FAILED'}")