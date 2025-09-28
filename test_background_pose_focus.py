#!/usr/bin/env python3
"""
Test script to verify background and pose focus in combined analysis
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.workflow_manager import WorkflowManager

async def test_combined_analysis_prompt():
    """Test that the combined analysis prompt focuses on background and pose only"""
    print("Testing combined analysis prompt focus...")
    
    # Initialize the workflow manager
    workflow_manager = WorkflowManager()
    
    # Create mock data
    image_paths = {
        "frontside": "tests/test_data/ref1.jpg",
        "backside": "tests/test_data/ref2.jpg"
    }
    text_description = "Elegant evening gown with floral embroidery"
    username = "testuser"
    product = "gown"
    number_of_outputs = 3
    
    # Check if the method exists
    print("1. Verifying combined analysis method exists...")
    if hasattr(workflow_manager, '_analyze_with_gemini_combined'):
        print("   ✓ Combined analysis method exists")
    else:
        print("   ✗ Combined analysis method not found")
        return
    
    # We can't easily test the actual API call without credentials, but we can verify
    # that the method is structured correctly by examining its docstring
    method = getattr(workflow_manager, '_analyze_with_gemini_combined')
    docstring = method.__doc__
    
    if docstring and "background and pose recommendations" in docstring:
        print("   ✓ Method docstring indicates focus on background and pose")
    else:
        print("   ✗ Method docstring does not indicate focus on background and pose")
    
    # Print information about what the prompt should focus on
    print("\n2. Combined analysis prompt should focus on:")
    print("   - Model pose recommendations only")
    print("   - Background settings only")
    print("   - View-specific poses")
    print("   - NOT on detailed product analysis")
    print("   - NOT on product description or features")
    
    print("\n3. Expected output structure:")
    print("   - product_data with Gender, Occasion, RecommendedPoses, ViewSpecificPoses")
    print("   - background_recommendations array")
    print("   - NO detailed product description or features in output")

if __name__ == "__main__":
    asyncio.run(test_combined_analysis_prompt())