#!/usr/bin/env python3
"""
Test the main API endpoint to debug the response issue
"""
import asyncio
import aiohttp
import aiofiles
import os
import json
from pathlib import Path

async def test_main_api():
    """Test the main API endpoint"""
    print("🧪 Testing Main API Endpoint")
    print("=" * 50)
    
    # Test data
    url = "http://localhost:8000/api/v1/generate"
    
    # Prepare form data
    data = aiohttp.FormData()
    data.add_field('text', 'Elegant dress for wedding occasions')
    data.add_field('username', 'testuser')
    data.add_field('product', 'kurti_lengha')
    data.add_field('generate_video', 'false')
    data.add_field('numberOfOutputs', '1')
    
    # Add frontside image
    frontside_path = "tests/test_data/ref1.jpg"
    if os.path.exists(frontside_path):
        async with aiofiles.open(frontside_path, 'rb') as f:
            frontside_content = await f.read()
        data.add_field('frontside', frontside_content, filename='ref1.jpg', content_type='image/jpeg')
        print(f"✅ Added frontside image: {frontside_path}")
    else:
        print(f"❌ Frontside image not found: {frontside_path}")
        return
    
    # Add detailview image
    detailview_path = "tests/test_data/usp1.jpg"
    if os.path.exists(detailview_path):
        async with aiofiles.open(detailview_path, 'rb') as f:
            detailview_content = await f.read()
        data.add_field('detailview', detailview_content, filename='usp1.jpg', content_type='image/jpeg')
        print(f"✅ Added detailview image: {detailview_path}")
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"\n🚀 Making API request to {url}")
            
            async with session.post(url, data=data) as response:
                print(f"📊 Status Code: {response.status}")
                print(f"📊 Content Type: {response.content_type}")
                
                # Get response text
                response_text = await response.text()
                print(f"📊 Response Length: {len(response_text)} characters")
                
                if response.status == 200:
                    try:
                        # Parse JSON response
                        result = json.loads(response_text)
                        print("\n✅ API Response (JSON):")
                        print(json.dumps(result, indent=2))
                        
                        # Check for results
                        print("\n🔍 Results Analysis:")
                        print(f"   Output Image URL: {result.get('output_image_url', 'None')}")
                        print(f"   Image Variations: {len(result.get('image_variations', []))} variations")
                        print(f"   Video URL: {result.get('output_video_url', 'None')}")
                        print(f"   Excel Report URL: {result.get('excel_report_url', 'None')}")
                        
                        if result.get('metadata'):
                            metadata = result['metadata']
                            print(f"   Request ID: {metadata.get('request_id', 'None')}")
                            print(f"   Total Variations: {metadata.get('total_variations', 'None')}")
                            
                            if 'analysis' in metadata:
                                analysis = metadata['analysis']
                                if 'product_data' in analysis:
                                    product_data = analysis['product_data']
                                    print(f"   SKU ID: {product_data.get('SKU_ID', 'None')}")
                                    print(f"   Description: {product_data.get('Description', 'None')[:50]}...")
                        
                    except json.JSONDecodeError as e:
                        print(f"❌ Failed to parse JSON response: {e}")
                        print(f"Raw response: {response_text[:500]}...")
                
                else:
                    print(f"❌ API Error (Status {response.status}):")
                    print(response_text)
                    
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_main_api())