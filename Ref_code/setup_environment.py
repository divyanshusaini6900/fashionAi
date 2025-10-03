import os
import json
from pathlib import Path

def create_env_file():
    """Create .env file template"""
    env_content = """# API Keys - Replace with your actual keys
OPENAI_API_KEY=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
REPLICATE_API_TOKEN=r8_Nqq9h7dHI3bTviOfEge3HmrLNPUcoQS23et0O
GEMINI_API_KEY=your-gemini-api-key-here

# Service API Key for x-api-key authentication
SERVICE_API_KEY=fashion-ai-service-key

# Optional: Other configurations
MODEL_NAME=gpt-4o
TEMPERATURE=0.7
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file template. Please update with your API keys.")

def create_sample_excel_files():
    """Create sample Excel files for testing"""
    import pandas as pd
    
    # Create directories
    Path("excel_files").mkdir(exist_ok=True)
    
    # Sample Shoes Excel structure
    shoes_data = {
        'Summary': pd.DataFrame({
            'Total Products': [0],
            'Last Updated': ['2024-01-01'],
            'Categories': ['Athletic, Casual, Formal']
        }),
        
        'Index': pd.DataFrame({
            'Sheet Name': ['Summary', 'Shoe Listing', 'FAQ', 'Image guidelines'],
            'Purpose': ['Overview', 'Product Data', 'Common Questions', 'Photo Requirements'],
            'Status': ['Active', 'Active', 'Active', 'Active']
        }),
        
        'Shoe Listing': pd.DataFrame({
            'Product ID': [],
            'Title': [],
            'Category': [],
            'Gender': [],
            'Size Range': [],
            'Price': [],
            'Description': [],
            'Color': [],
            'Material': [],
            'Brand': [],
            'Image URLs': []
        }),
        
        'FAQ': pd.DataFrame({
            'Question': [
                'What size format to use?',
                'How to categorize athletic shoes?',
                'Required vs optional fields?'
            ],
            'Answer': [
                'Use US sizing (7, 8, 9, etc.)',
                'Running, Basketball, Training, Cross-training',
                'Required: Title, Category, Gender, Price. Optional: Brand, Description'
            ],
            'Category': ['Sizing', 'Categorization', 'Data Entry']
        }),
        
        'Image guidelines': pd.DataFrame({
            'View Type': ['Front View', 'Side View', 'Back View', 'Detail Shot'],
            'Requirements': [
                'Straight front angle, both shoes visible',
                'Left or right profile, clean background',  
                'Rear view showing heel and back design',
                'Close-up of key features (logo, texture, sole)'
            ],
            'Background': ['White/Gray', 'White/Gray', 'White/Gray', 'White/Gray'],
            'Model Requirements': [
                'Professional model, demographic appropriate',
                'Natural walking pose or standing',
                'Standing pose from behind',
                'Product focus, minimal model visibility'
            ]
        })
    }
    
    # Create Shoes Excel file
    with pd.ExcelWriter('excel_files/shoes_data.xlsx', engine='openpyxl') as writer:
        for sheet_name, df in shoes_data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    # Sample Jewellery Excel structure
    jewellery_data = {
        'Summary': pd.DataFrame({
            'Total Products': [0],
            'Last Updated': ['2024-01-01'],
            'Categories': ['Rings, Necklaces, Earrings, Bracelets']
        }),
        
        'Index': pd.DataFrame({
            'Sheet Name': ['Summary', 'Jewellery Listing', 'FAQ', 'Image guidelines'],
            'Purpose': ['Overview', 'Product Data', 'Common Questions', 'Photo Requirements'],
            'Status': ['Active', 'Active', 'Active', 'Active']
        }),
        
        'Jewellery Listing': pd.DataFrame({
            'Product ID': [],
            'Title': [],
            'Category': [],
            'Gender': [],
            'Material': [],
            'Price': [],
            'Description': [],
            'Stone Type': [],
            'Size/Dimensions': [],
            'Style': [],
            'Collection': [],
            'Image URLs': []
        }),
        
        'FAQ': pd.DataFrame({
            'Question': [
                'How to describe materials?',
                'Ring sizing format?',
                'Stone quality description?'
            ],
            'Answer': [
                'Use full material names: 14K Gold, Sterling Silver, etc.',
                'Use US ring sizes: 5, 6, 7, etc.',
                'Specify cut, color, clarity when known'
            ],
            'Category': ['Materials', 'Sizing', 'Quality']
        }),
        
        'Image guidelines': pd.DataFrame({
            'View Type': ['Front View', 'Profile View', 'Detail Shot', 'Lifestyle Shot'],
            'Requirements': [
                'Direct front view showing main design',
                'Side angle showing depth and profile',
                'Close-up of stones, engravings, clasps',
                'Worn on model showing scale and style'
            ],
            'Background': ['White/Neutral', 'White/Neutral', 'White/Neutral', 'Lifestyle Setting'],
            'Model Requirements': [
                'Clean hands/neck/ears, demographic appropriate',
                'Natural positioning, good lighting',
                'Focus on product details',
                'Lifestyle context, natural interaction'
            ]
        })
    }
    
    # Create Jewellery Excel file
    with pd.ExcelWriter('excel_files/jewellery_data.xlsx', engine='openpyxl') as writer:
        for sheet_name, df in jewellery_data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print("✅ Created sample Excel files in excel_files/ directory")

def create_test_images_structure():
    """Create test images directory structure"""
    test_dirs = [
        "test_images/shoes",
        "test_images/jewellery", 
        "test_images/mixed"
    ]
    
    for dir_path in test_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Create a README for test images
    readme_content = """# Test Images Directory

Add your test product images here:

## Structure:
- shoes/ - Put shoe product images here
- jewellery/ - Put jewellery product images here  
- mixed/ - Put mixed/unclear product images here

## Supported formats:
- JPG, JPEG, PNG
- Recommended size: 1024x1024 or higher
- Clear, well-lit product photos work best

## Naming suggestions:
- shoe_mens_sneaker_01.jpg
- jewellery_womens_ring_01.jpg
- product_description_angle.jpg

## Note:
The system will analyze these images along with your text description
to determine product category and generate appropriate listings.
"""
    
    with open("test_images/README.md", "w") as f:
        f.write(readme_content)
    
    print("✅ Created test_images directory structure")

def create_quick_test_script():
    """Create a quick test script"""
    test_script = '''#!/usr/bin/env python3
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
        
        print("\\n🎉 Test completed successfully!")
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
'''
    
    with open("quick_test.py", "w") as f:
        f.write(test_script)
    
    print("✅ Created quick_test.py script")

def main():
    """Setup complete environment"""
    print("🔧 Setting up Multi-Agent Product Listing System Environment")
    print("=" * 60)
    
    # Create all necessary files and directories
    create_env_file()
    create_sample_excel_files()  
    create_test_images_structure()
    create_quick_test_script()
    
    print("\n✅ Environment setup complete!")
    print("\n📋 Next steps:")
    print("1. Install requirements: pip install -r requirements.txt")
    print("2. Update .env file with your API keys")
    print("3. Add test images to test_images/ directory")
    print("4. Run: python quick_test.py")
    print("\n🚀 Happy testing!")

if __name__ == "__main__":
    main()