#!/usr/bin/env python3
"""
Direct workflow test to bypass potential API issues
"""
import asyncio
import os
import sys
import logging

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from app.services.workflow_manager import WorkflowManager
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_direct_workflow():
    """Test the workflow manager directly"""
    print("🧪 Testing Workflow Manager Directly")
    print("=" * 50)
    
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
        print(f"✅ Found image: {key} -> {path}")
    
    try:
        # Initialize workflow manager
        print(f"\n🔧 Initializing WorkflowManager...")
        workflow_manager = WorkflowManager()
        
        # Test parameters
        text_description = "Elegant dress for wedding occasions"
        request_id = "test-workflow-123"
        username = "Mene"
        product = "kurti_lengha"
        generate_video = False
        number_of_outputs = 1
        
        print(f"\n📋 Test Parameters:")
        print(f"   Text: '{text_description}'")
        print(f"   Username: '{username}'")
        print(f"   Product: '{product}'")
        print(f"   Number of Outputs: {number_of_outputs}")
        print(f"   Generate Video: {generate_video}")
        print(f"   Request ID: {request_id}")
        
        # Process the request
        print(f"\n🚀 Processing workflow...")
        result = await workflow_manager.process_request(
            image_paths=image_paths,
            text_description=text_description,
            request_id=request_id,
            username=username,
            product=product,
            generate_video=generate_video,
            number_of_outputs=number_of_outputs
        )
        
        print(f"\n✅ Workflow completed successfully!")
        print(f"📊 Result Structure:")
        
        # Analyze results
        print(f"   Output Image URL: {result.get('output_image_url', 'None')}")
        print(f"   Image Variations: {len(result.get('image_variations', []))} variations")
        print(f"   Video URL: {result.get('output_video_url', 'None')}")
        print(f"   Excel Report URL: {result.get('excel_report_url', 'None')}")
        
        metadata = result.get('metadata', {})
        print(f"   Request ID: {metadata.get('request_id', 'None')}")
        print(f"   Total Variations: {metadata.get('total_variations', 'None')}")
        
        if 'analysis' in metadata:
            analysis = metadata['analysis']
            if 'product_data' in analysis:
                product_data = analysis['product_data']
                print(f"   SKU ID: {product_data.get('SKU_ID', 'None')}")
                print(f"   Description: {product_data.get('Description', 'None')[:60]}...")
                print(f"   Gender: {product_data.get('Gender', 'None')}")
                print(f"   Occasion: {product_data.get('Occasion', 'None')}")
        
        print(f"\n🎯 DIAGNOSIS:")
        print("=" * 50)
        
        # Check if this matches expected GenerationResponse schema
        expected_fields = ['output_image_url', 'image_variations', 'output_video_url', 'excel_report_url', 'metadata']
        missing_fields = [field for field in expected_fields if field not in result]
        
        if missing_fields:
            print(f"❌ Missing expected fields: {missing_fields}")
        else:
            print(f"✅ All expected fields present")
            
        # Check field types
        if result.get('output_image_url') is None:
            print(f"❌ output_image_url is None (should be string)")
        elif isinstance(result.get('output_image_url'), str):
            print(f"✅ output_image_url is string: {result['output_image_url'][:50]}...")
        
        if result.get('excel_report_url') is None:
            print(f"❌ excel_report_url is None (should be string)")
        elif isinstance(result.get('excel_report_url'), str):
            print(f"✅ excel_report_url is string: {result['excel_report_url'][:50]}...")
            
        return result
        
    except Exception as e:
        print(f"\n❌ Workflow failed: {str(e)}")
        print(f"🔍 Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(test_direct_workflow())
    if result:
        print(f"\n🎉 Direct workflow test: SUCCESS")
    else:
        print(f"\n💥 Direct workflow test: FAILED")