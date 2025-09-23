#!/usr/bin/env python3
"""
Test direct output folder storage functionality and verify single person generation
"""
import asyncio
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from app.services.workflow_manager import WorkflowManager
from app.core.config import settings

async def test_direct_output_storage():
    """Test direct output folder storage and single person generation"""
    print("🧪 Testing Direct Output Folder Storage & Single Person Generation")
    print("=" * 60)
    
    # Test data
    image_paths = {
        "frontside": "tests/test_data/ref1.jpg",
        "detailview": "tests/test_data/usp1.jpg"
    }
    
    # Verify images exist
    for key, path in image_paths.items():
        if not os.path.exists(path):
            print(f"❌ Missing image: {path}")
            return
    
    print(f"✅ Current storage setting: USE_LOCAL_STORAGE = {settings.USE_LOCAL_STORAGE}")
    print(f"✅ Output directory: {settings.LOCAL_OUTPUT_DIR}")
    print(f"✅ Image generation mode: {'Gemini' if settings.USE_GEMINI_FOR_IMAGES else 'Replicate'}")
    
    try:
        # Initialize workflow manager
        workflow_manager = WorkflowManager()
        
        # Test parameters
        text_description = ""
        request_id = "single-person-test"
        username = "Mene"
        product = "Kurti lengha"
        
        print(f"\n📋 Test Parameters:")
        print(f"   Request ID: {request_id}")
        print(f"   Product: {product}")
        print(f"   Username: {username}")
        print(f"   Expected Output: {os.path.abspath(settings.LOCAL_OUTPUT_DIR)}")
        print(f"   Test Focus: Verify only ONE person appears in generated images")
        
        # Check if output directory exists
        output_dir = os.path.abspath(settings.LOCAL_OUTPUT_DIR)
        if not os.path.exists(output_dir):
            print(f"   📁 Creating output directory: {output_dir}")
            os.makedirs(output_dir, exist_ok=True)
        else:
            print(f"   📁 Output directory exists: {output_dir}")
        
        # List files before processing
        files_before = set(os.listdir(output_dir)) if os.path.exists(output_dir) else set()
        print(f"   📋 Files before: {len(files_before)} files")
        
        # Process the request
        print(f"\n🚀 Processing workflow with single person generation...")
        print(f"   📝 Expected prompt features:")
        print(f"      - 'A single Indian woman model'")
        print(f"      - 'Show ONLY ONE person in the image'")
        print(f"      - 'No duplicate or repeated figures'")
        
        result = await workflow_manager.process_request(
            image_paths=image_paths,
            text_description=text_description,
            request_id=request_id,
            username=username,
            product=product,
            generate_video=False,
            number_of_outputs=3
        )
        
        print(f"\n✅ Workflow completed!")
        
        # Check results
        output_url = result.get('output_image_url', '')
        excel_url = result.get('excel_report_url', '')
        variations = result.get('image_variations', [])
        
        print(f"\n📊 Generation Results:")
        print(f"   Primary Image: {output_url}")
        print(f"   Excel Report: {excel_url}")
        print(f"   Image Variations: {len(variations)} variations")
        
        # Verify single person generation
        print(f"\n👤 Single Person Verification:")
        print(f"   🎯 All generated images should contain ONLY ONE person")
        print(f"   🚫 No duplicate or repeated figures should appear")
        print(f"   ✨ Images should show proper grammar: 'single Indian woman model'")
        
        # Check if paths are direct file paths (not HTTP URLs)
        if settings.USE_LOCAL_STORAGE:
            print(f"\n📁 File Path Analysis:")
            
            # Check primary image
            if output_url and os.path.isabs(output_url) and os.path.exists(output_url):
                print(f"   ✅ Primary image saved directly: {output_url}")
            else:
                print(f"   ❌ Primary image path issue: {output_url}")
            
            # Check Excel report
            if excel_url and os.path.isabs(excel_url) and os.path.exists(excel_url):
                print(f"   ✅ Excel report saved directly: {excel_url}")
            else:
                print(f"   ❌ Excel report path issue: {excel_url}")
            
            # Check variations
            for variation in variations:
                if variation and os.path.isabs(variation) and os.path.exists(variation):
                    print(f"   ✅ Variation saved directly: {os.path.basename(variation)}")
                else:
                    print(f"   ❌ Variation path issue: {variation}")
        
        # List files after processing
        files_after = set(os.listdir(output_dir)) if os.path.exists(output_dir) else set()
        new_files = files_after - files_before
        
        print(f"\n📁 Output Directory Analysis:")
        print(f"   📋 Files after: {len(files_after)} files")
        print(f"   🆕 New files created: {len(new_files)} files")
        
        if new_files:
            print(f"\n   📸 Generated Images (check for single person):")
            for file in sorted(new_files):
                file_path = os.path.join(output_dir, file)
                file_size = os.path.getsize(file_path)
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    print(f"      🖼️  {file} ({file_size:,} bytes) - VERIFY: Only one person visible")
                else:
                    print(f"      📄 {file} ({file_size:,} bytes)")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print(f"🎯 Single Person Generation & Direct Output Test")
    print(f"Current setting: USE_LOCAL_STORAGE = {settings.USE_LOCAL_STORAGE}")
    print(f"Image generation: {'Gemini' if settings.USE_GEMINI_FOR_IMAGES else 'Replicate'}")
    print(f"Output folder: {os.path.abspath(settings.LOCAL_OUTPUT_DIR)}")
    print(f"")
    
    result = asyncio.run(test_direct_output_storage())
    
    if result:
        print(f"\n🎉 Single person generation test completed successfully!")
        print(f"\n💡 Generated images saved directly to:")
        print(f"   📁 {os.path.abspath(settings.LOCAL_OUTPUT_DIR)}")
        print(f"\n🔍 Manual Verification Required:")
        print(f"   👀 Please check each generated image to confirm:")
        print(f"   ✅ Only ONE person appears in each image")
        print(f"   ✅ No duplicate or repeated figures")
        print(f"   ✅ Professional fashion photography quality")
    else:
        print(f"\n💥 Single person generation test failed!")