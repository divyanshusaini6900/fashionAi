import asyncio
import base64
import io
import json
import os
import random
import re
from typing import Dict, List, Optional, Tuple, Any
from PIL import Image
import pandas as pd
import openpyxl
import requests
import replicate

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("💡 Tip: Install python-dotenv for .env file support: pip install python-dotenv")

# Updated imports for latest autogen v0.4
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Configuration
MODEL_CLIENT = OpenAIChatCompletionClient(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY"),
)

class InputHandler:
    """Handle image and text inputs for testing"""
    
    @staticmethod
    def encode_image_to_base64(image_path: str) -> str:
        """Convert image file to base64 string"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image {image_path}: {e}")
            return ""
    
    @staticmethod
    def process_multiple_images(image_paths: List[str]) -> List[Dict]:
        """Process multiple images for agent consumption"""
        processed_images = []
        for i, path in enumerate(image_paths):
            if os.path.exists(path):
                base64_image = InputHandler.encode_image_to_base64(path)
                if base64_image:
                    processed_images.append({
                        "image_id": f"image_{i+1}",
                        "path": path,
                        "base64": base64_image,
                        "type": "image"
                    })
            else:
                print(f"Warning: Image file {path} not found")
        return processed_images
    
    @staticmethod
    def create_test_input() -> Tuple[List[Dict], str]:
        """Create test input - looks for actual images in test_images"""
        from pathlib import Path
        
        # Look for actual images
        image_paths = []
        for ext in ['jpg', 'jpeg', 'png']:
            image_paths.extend(Path("test_images").glob(f"**/*.{ext}"))
        
        # Convert to strings and take first 4
        image_paths = [str(p) for p in image_paths[:4]]
        
        # Example rough text
        rough_text = """
        Brown leather dress shoes for men
        Size 10.5 US
        Oxford style with laces
        Genuine leather upper
        Professional business wear
        Price around $120
        """
        
        processed_images = InputHandler.process_multiple_images(image_paths)
        return processed_images, rough_text.strip()

class ExcelProcessor:
    """Fixed Excel processor that actually reads and maps data correctly"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.sheets_data = {}
        self.exact_columns = {}
        if os.path.exists(file_path):
            self._load_excel_data()
    
    def _load_excel_data(self):
        """Load Excel data and get exact column structure"""
        try:
            # Read all sheets
            excel_file = pd.ExcelFile(self.file_path)
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(self.file_path, sheet_name=sheet_name)
                self.sheets_data[sheet_name] = df
                
                # Store exact column names for listing sheets
                if 'listing' in sheet_name.lower():
                    self.exact_columns[sheet_name] = list(df.columns)
                    print(f"📊 Found {sheet_name} with columns: {list(df.columns)}")
                    
        except Exception as e:
            print(f"Error loading Excel file {self.file_path}: {e}")
    
    def get_exact_structure(self) -> Dict[str, Any]:
        """Get the exact Excel structure for agents to follow"""
        structure = {
            "available_sheets": list(self.sheets_data.keys()),
            "listing_sheets": {},
            "image_guidelines": [],
            "faq_data": []
        }
        
        # Get listing sheet structure
        for sheet_name, df in self.sheets_data.items():
            if 'listing' in sheet_name.lower():
                structure["listing_sheets"][sheet_name] = {
                    "exact_columns": list(df.columns),
                    "total_rows": len(df),
                    "sample_data": df.head(1).to_dict('records') if len(df) > 0 else []
                }
        
        # Get image guidelines
        if 'Image guidelines' in self.sheets_data:
            structure["image_guidelines"] = self.sheets_data['Image guidelines'].to_dict('records')
        
        # Get FAQ
        if 'FAQ' in self.sheets_data:
            structure["faq_data"] = self.sheets_data['FAQ'].to_dict('records')
        
        return structure
    
    def add_new_row(self, sheet_name: str, data_dict: Dict) -> bool:
        """Add new row to Excel with intelligent Flipkart column mapping"""
        try:
            if sheet_name not in self.sheets_data:
                print(f"❌ Sheet '{sheet_name}' not found in Excel")
                return False
            
            df = self.sheets_data[sheet_name]
            exact_columns = list(df.columns)
            
            print(f"📋 Target sheet: {sheet_name}")
            print(f"📊 Total Flipkart columns: {len(exact_columns)}")
            
            # Create new row with intelligent mapping
            new_row_data = {}
            filled_fields = 0
            
            for col in exact_columns:
                value = ""
                
                # Direct mapping first
                if col in data_dict:
                    value = data_dict[col]
                    filled_fields += 1
                # Smart mapping for common fields
                elif col == "Description" and "Description" in data_dict:
                    value = data_dict["Description"]
                    filled_fields += 1
                elif col == "Main Image URL" and "Main Image URL" in data_dict:
                    value = data_dict["Main Image URL"]
                    filled_fields += 1
                elif "Image URL" in col and "generated_image_urls" in data_dict:
                    # Map generated images to image URL fields
                    urls = data_dict["generated_image_urls"]
                    if col == "Main Image URL" and len(urls) > 0:
                        value = urls[0]
                        filled_fields += 1
                    elif col == "Other Image URL 1" and len(urls) > 1:
                        value = urls[1]
                        filled_fields += 1
                    elif col == "Other Image URL 2" and len(urls) > 2:
                        value = urls[2]
                        filled_fields += 1
                    elif col == "Other Image URL 3" and len(urls) > 3:
                        value = urls[3]
                        filled_fields += 1
                
                new_row_data[col] = value
            
            print(f"📝 Successfully mapped {filled_fields}/{len(exact_columns)} fields")
            print(f"📋 Sample mapped data: {dict(list(new_row_data.items())[:5])}")
            
            # Add the new row
            new_row_df = pd.DataFrame([new_row_data])
            updated_df = pd.concat([df, new_row_df], ignore_index=True)
            
            # Save back to Excel
            with pd.ExcelWriter(self.file_path, mode='a', if_sheet_exists='replace') as writer:
                for existing_sheet, existing_df in self.sheets_data.items():
                    if existing_sheet == sheet_name:
                        updated_df.to_excel(writer, sheet_name=existing_sheet, index=False)
                    else:
                        existing_df.to_excel(writer, sheet_name=existing_sheet, index=False)
            
            self.sheets_data[sheet_name] = updated_df
            print(f"✅ Added new row to {sheet_name}. Total rows: {len(updated_df)}")
            print(f"💡 Data quality: {filled_fields}/{len(exact_columns)} fields populated ({filled_fields/len(exact_columns)*100:.1f}%)")
            return True
            
        except Exception as e:
            print(f"❌ Error adding row: {e}")
            import traceback
            traceback.print_exc()
            return False

class ImageGenerator:
    """Fixed image generator that actually uses reference images properly"""
    
    def __init__(self):
        # Use a model that supports reference images properly
        self.model = "stability-ai/stable-diffusion-xl-base-1.0"
        
    def create_prompt_with_product_wearing(self, target_demo: str, view_angle: str, product_category: str = "shoes") -> str:
        """Create prompts showing models wearing the specific product"""
        
        if "man" in target_demo.lower():
            model = "professional male model"
        elif "woman" in target_demo.lower():
            model = "professional female model"
        else:
            model = "professional model"
        
        if product_category.lower() == "shoes":
            scenarios = [
                f"{model} wearing the shoes, standing confidently",
                f"{model} walking while wearing the shoes",
                f"{model} posing with the shoes clearly visible",
                f"close-up of {model}'s feet wearing the shoes"
            ]
        else:  # jewelry
            scenarios = [
                f"{model} wearing the jewelry elegantly",
                f"{model} displaying the jewelry",
                f"close-up of {model} wearing the jewelry",
                f"{model} showcasing the jewelry piece"
            ]
        
        scenario = random.choice(scenarios)
        
        prompt = f"""
        {scenario}, {view_angle}, professional product photography, 
        white studio background, high quality, commercial style, 
        product clearly visible and prominent, e-commerce photography
        """.strip()
        
        return prompt
    
    async def generate_with_reference(self, prompt: str, reference_images: List[Dict] = None) -> Optional[str]:
        """Generate image using reference image properly"""
        try:
            replicate_token = os.getenv("REPLICATE_API_TOKEN")
            if not replicate_token:
                print("⚠️  REPLICATE_API_TOKEN not set")
                return None
            
            client = replicate.Client(api_token=replicate_token)
            
            if reference_images and len(reference_images) > 0:
                # Try with ControlNet for better reference adherence
                print("🎨 Generating with product reference...")
                
                try:
                    # Use a ControlNet model for better reference image handling
                    controlnet_model = "jagilley/controlnet-canny"
                    
                    output = await asyncio.to_thread(
                        client.run,
                        controlnet_model,
                        input={
                            "image": f"data:image/jpeg;base64,{reference_images[0]['base64']}",
                            "prompt": prompt,
                            "num_outputs": 1,
                            "guidance_scale": 7.5,
                            "prompt_strength": 0.8,
                            "num_inference_steps": 20
                        }
                    )
                    
                    if output and len(output) > 0:
                        result_url = str(output[0])
                        print(f"✅ Generated with reference: {result_url[:50]}...")
                        return result_url
                        
                except Exception as controlnet_error:
                    print(f"⚠️  ControlNet failed: {controlnet_error}")
                    print("🔄 Trying alternative method...")
                
                # Fallback: Try img2img approach
                try:
                    img2img_model = "stability-ai/sdxl"
                    
                    enhanced_prompt = f"{prompt}. Product should match the reference image style and appearance exactly."
                    
                    output = await asyncio.to_thread(
                        client.run,
                        img2img_model,
                        input={
                            "image": f"data:image/jpeg;base64,{reference_images[0]['base64']}",
                            "prompt": enhanced_prompt,
                            "strength": 0.7,  # Keep some reference characteristics
                            "guidance_scale": 7.5,
                            "num_inference_steps": 25
                        }
                    )
                    
                    if output and len(output) > 0:
                        result_url = str(output[0])
                        print(f"✅ Generated with img2img: {result_url[:50]}...")
                        return result_url
                        
                except Exception as img2img_error:
                    print(f"⚠️  img2img failed: {img2img_error}")
            
            # Final fallback: Generate without reference
            print("🔄 Generating without reference...")
            basic_model = "stability-ai/stable-diffusion-xl-base-1.0"
            
            output = await asyncio.to_thread(
                client.run,
                basic_model,
                input={
                    "prompt": prompt,
                    "width": 1024,
                    "height": 1024,
                    "num_outputs": 1,
                    "guidance_scale": 7.5,
                    "num_inference_steps": 25
                }
            )
            
            if output and len(output) > 0:
                result_url = str(output[0])
                print(f"✅ Generated without reference: {result_url[:50]}...")
                return result_url
            
            return None
            
        except Exception as e:
            print(f"❌ Image generation error: {e}")
            return None

# Agents with very specific instructions

planner_agent = AssistantAgent(
    name="planner",
    model_client=MODEL_CLIENT,
    system_message="""You are a product analysis agent. Analyze the provided product information and respond in this EXACT format:

CATEGORY: [shoes|jewellery]
DEMOGRAPHIC: [man|woman|child]
ATTRIBUTES: key product features from the text
CONFIDENCE: [high|medium|low]

Example:
CATEGORY: shoes
DEMOGRAPHIC: man  
ATTRIBUTES: brown leather dress shoes, size 10.5, oxford style, business wear
CONFIDENCE: high

Be precise and follow this format exactly."""
)

data_extraction_agent = AssistantAgent(
    name="data_extractor",
    model_client=MODEL_CLIENT,
    system_message="""You are a Flipkart product data extraction specialist. You must generate data for EXACT Flipkart column names with specific requirements:

CRITICAL: Output ONLY valid JSON with exact Flipkart column names. No explanations, no markdown, just JSON.

CHARACTER LIMITS & SEO REQUIREMENTS:
- Brand: Max 50 chars, brand name only
- Article Number: 5-15 alphanumeric chars (e.g., RBK123A, NK456B)
- Size: Numeric size (e.g., 6, 7, 8, 9, 10, 11, 12)
- Brand Color: Max 30 chars, creative color names (e.g., "Midnight Black", "Ocean Blue")
- Color: Primary colors only (Black, Brown, White, Red, Blue, etc.)
- Model Name: Max 50 chars, catchy model name (e.g., "AirMax Pro", "ClassicWalk Elite")
- Description: 500-2000 chars, SEO-friendly, keyword-rich, compelling product description
- Search Keywords: Max 5 keywords, comma-separated, high-search terms
- Key Features: Bullet points of top 3-5 features

FLIPKART FIELD MAPPING:
{
  "Listing Status": "Active",
  "MRP (INR)": 2999,
  "Your selling price (INR)": 2499,
  "Fullfilment by": "FLIPKART",
  "Procurement type": "Regular",
  "Procurement SLA (DAY)": 2,
  "Stock": 50,
  "Shipping provider": "Flipkart",
  "Country Of Origin": "IN",
  "Brand": "[Extract/Generate Brand Name - Max 50 chars]",
  "Article Number": "[Generate unique code like RBK123A]",
  "Size": "[Extract size number]",
  "Size - Measuring Unit": "[UK/India] or [Euro]",
  "UK/India Size": "[UK/India size number]",
  "Euro Size": "[Euro size number]", 
  "Brand Color": "[Creative color name - Max 30 chars]",
  "Style Code": "[Generate style code from article number]",
  "Color": "[Primary color]",
  "Ideal For": "[Men] or [Women] based on product",
  "Occasion": "[Casual/Formal/Sports/Ethnic based on shoe type]",
  "Outer Material": "[Leather/Canvas/Synthetic/Mesh based on description]",
  "Type for Casual": "[Sneakers/Loafers/Slip On] or NA",
  "Type for Ethnic": "[Jutis/Mojaris] or NA", 
  "Type for Formal": "[Oxfords/Derbys/Brogues] or NA",
  "Type for Sports": "[Running Shoes/Training Shoes] or NA",
  "Heel Height (inch)": 1.0,
  "Main Image URL": "[First generated image URL]",
  "Other Image URL 1": "[Second generated image URL]",
  "Other Image URL 2": "[Third generated image URL]",
  "Group ID": "[Generate group ID like GRP001]",
  "Shoe Type": "[Based on product type]",
  "Model Name": "[Catchy model name - Max 50 chars, SEO-friendly]",
  "Leather Type": "[Genuine/Synthetic/Nubuck] or blank",
  "Sole Material": "[Rubber/EVA/TPU based on shoe type]",
  "Pack of": 1,
  "Closure": "[Lace Up/Slip On/Velcro based on shoe]",
  "Tip Shape": "[Round/Pointed/Square based on style]",
  "Upper Pattern": "[Solid/Textured based on description]",
  "Care Instructions": "Wipe with clean, dry cloth",
  "Inner Material": "[Fabric/Leather based on quality]",
  "Weight (g)": 800,
  "Sales Package": "1 Pair of Shoes",
  "Description": "[500-2000 chars, SEO-optimized, keyword-rich description]",
  "Search Keywords": "[5 high-search keywords separated by ::]",
  "Key Features": "[Top 3-5 features separated by ::]",
  "Pack of": 1
}

EXAMPLE for Brown Leather Dress Shoes:
{
  "Listing Status": "Active",
  "MRP (INR)": 4999,
  "Your selling price (INR)": 3999,
  "Brand": "ClassicCraft",
  "Article Number": "CC789BR",
  "Size": 9,
  "Brand Color": "Rich Chocolate Brown",
  "Color": "Brown", 
  "Model Name": "Executive Oxford Elite",
  "Description": "Elevate your professional wardrobe with these premium brown leather Oxford shoes. Crafted from genuine leather with a classic design, these formal shoes feature traditional lace-up closure and cushioned insole for all-day comfort. Perfect for office meetings, business events, and formal occasions. The durable leather upper and rubber sole ensure long-lasting wear while maintaining a sophisticated appearance.",
  "Search Keywords": "leather shoes::formal shoes::oxford shoes::brown shoes::dress shoes",
  "Key Features": "Genuine leather upper::Cushioned insole::Classic Oxford design::Durable rubber sole::Professional appearance"
}

Generate realistic, market-appropriate data for each field based on the product description provided."""
)

validation_agent = AssistantAgent(
    name="validator", 
    model_client=MODEL_CLIENT,
    system_message="""You validate product data completeness. Check if all required fields are filled properly.

Respond in this EXACT format:
STATUS: [APPROVED|NEEDS_REVISION]
MISSING: [list any missing required fields]
ISSUES: [list any data quality issues]
RECOMMENDATION: [what needs to be fixed]

Be specific about what's missing or wrong."""
)

class ProductListingSystem:
    """Fixed system that actually works with proper data extraction"""
    
    def __init__(self, shoe_excel_path: str, jewellery_excel_path: str):
        self.shoe_processor = ExcelProcessor(shoe_excel_path) if shoe_excel_path else None
        self.jewellery_processor = ExcelProcessor(jewellery_excel_path) if jewellery_excel_path else None
        self.image_generator = ImageGenerator()
    
    def parse_agent_response(self, response_text: str, expected_format: str = "category") -> Dict:
        """Parse agent responses with improved JSON handling"""
        result = {}
        
        if expected_format == "category":
            # Parse planner response
            for line in response_text.split('\n'):
                if line.startswith('CATEGORY:'):
                    result['category'] = line.split(':', 1)[1].strip()
                elif line.startswith('DEMOGRAPHIC:'):
                    result['demographic'] = line.split(':', 1)[1].strip()
                elif line.startswith('ATTRIBUTES:'):
                    result['attributes'] = line.split(':', 1)[1].strip()
                elif line.startswith('CONFIDENCE:'):
                    result['confidence'] = line.split(':', 1)[1].strip()
        
        elif expected_format == "json":
            # Parse JSON from data extraction with better error handling
            try:
                # First try to find complete JSON block
                json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
                json_matches = re.findall(json_pattern, response_text, re.DOTALL)
                
                for json_match in json_matches:
                    try:
                        parsed = json.loads(json_match)
                        if isinstance(parsed, dict) and len(parsed) > 5:  # Should have multiple Flipkart fields
                            result = parsed
                            break
                    except json.JSONDecodeError:
                        continue
                
                # If no good JSON found, try to extract from text
                if not result:
                    print("⚠️  No valid JSON found, attempting text extraction...")
                    # Extract key-value pairs from text
                    lines = response_text.split('\n')
                    for line in lines:
                        if ':' in line and not line.strip().startswith(('//','#','*')):
                            try:
                                key, value = line.split(':', 1)
                                key = key.strip().strip('"').strip("'")
                                value = value.strip().strip(',').strip('"').strip("'")
                                if key and value and value != "":
                                    result[key] = value
                            except:
                                continue
                
                print(f"📋 Parsed {len(result)} fields from agent response")
                
            except Exception as e:
                print(f"⚠️  JSON parsing error: {e}")
                print(f"Raw response: {response_text[:500]}...")
                
        return result
    
    async def process_product(self, images: List[Dict], product_text: str) -> Dict:
        """Process product with proper data extraction and image generation"""
        
        # Step 1: Analyze product category
        print("🔍 Analyzing product category...")
        
        analysis_prompt = f"""
        Analyze this product:
        Text: {product_text}
        Images: {len(images)} product images provided
        
        Determine the category and target demographic.
        """
        
        planner_team = RoundRobinGroupChat([planner_agent], termination_condition=MaxMessageTermination(2))
        planner_result = await planner_team.run(task=analysis_prompt)
        
        # Parse the planner response
        analysis = self.parse_agent_response(str(planner_result.messages[-1].content), "category")
        category = analysis.get('category', 'shoes')
        demographic = analysis.get('demographic', 'man')
        
        print(f"✅ Detected: {category} for {demographic}")
        
        # Step 2: Get Excel structure
        if category == 'shoes':
            processor = self.shoe_processor
            target_sheet = 'Shoe Listing'
        else:
            processor = self.jewellery_processor  
            target_sheet = 'Jewellery Listing'
        
        if not processor:
            print("❌ No Excel processor available")
            return {"status": "failed", "reason": "No Excel file"}
        
        excel_structure = processor.get_exact_structure()
        target_columns = excel_structure['listing_sheets'].get(target_sheet, {}).get('exact_columns', [])
        
        print(f"📊 Target columns: {target_columns}")
        
        # Step 3: Extract data for exact Flipkart columns
        print("📝 Extracting data for Flipkart marketplace...")
        
        # Get the exact Flipkart columns
        flipkart_columns = excel_structure['listing_sheets'].get(target_sheet, {}).get('exact_columns', [])
        
        extraction_prompt = f"""
        Generate Flipkart marketplace data for this product:
        
        Product Text: {product_text}
        Product Category: {category}
        Target Demographic: {demographic}
        
        CRITICAL: Generate data for these EXACT Flipkart columns with proper character limits and SEO optimization:
        
        Required Flipkart Columns: {flipkart_columns}
        
        Follow the character limits and SEO requirements in your system message.
        Generate realistic, market-ready data for Indian e-commerce.
        
        Output ONLY valid JSON with exact column names from the list above.
        """
        
        extractor_team = RoundRobinGroupChat([data_extraction_agent], termination_condition=MaxMessageTermination(3))
        extraction_result = await extractor_team.run(task=extraction_prompt)
        
        # Parse extracted data
        extracted_data = self.parse_agent_response(str(extraction_result.messages[-1].content), "json")
        
        # Verify we got data for key fields
        key_fields = ['Brand', 'Model Name', 'Description', 'Search Keywords', 'MRP (INR)']
        filled_key_fields = sum(1 for field in key_fields if field in extracted_data and extracted_data[field])
        
        print(f"📋 Extracted data for {len(extracted_data)} fields")
        print(f"📊 Key fields populated: {filled_key_fields}/{len(key_fields)}")
        print(f"📝 Sample data: Brand='{extracted_data.get('Brand', 'N/A')}', Model='{extracted_data.get('Model Name', 'N/A')}'")
        
        # Step 4: Generate Flipkart-compliant images
        print("🎨 Generating Flipkart-compliant product images...")
        
        # Generate specific image types required by Flipkart
        image_requirements = [
            {"view": "main diagonal view", "desc": "Primary product image - diagonal view showing both side and top"},
            {"view": "front and sole view", "desc": "Front view with sole visible"},
            {"view": "model shot view", "desc": "Lifestyle shot with model wearing the product"},
            {"view": "zoomed detail view", "desc": "Close-up of key product features"}
        ]
        
        generated_images = []
        for req in image_requirements:
            prompt = self.image_generator.create_prompt_with_product_wearing(
                demographic, req["view"], category
            )
            print(f"   Generating {req['view']}...")
            
            img_url = await self.image_generator.generate_with_reference(prompt, images)
            if img_url:
                generated_images.append(img_url)
                print(f"   ✅ {req['view']}: {img_url[:50]}...")
            else:
                print(f"   ❌ Failed: {req['view']}")
        
        # Add generated images to extracted data
        if generated_images:
            extracted_data['Main Image URL'] = generated_images[0] if len(generated_images) > 0 else ""
            extracted_data['Other Image URL 1'] = generated_images[1] if len(generated_images) > 1 else ""
            extracted_data['Other Image URL 2'] = generated_images[2] if len(generated_images) > 2 else ""
            extracted_data['Other Image URL 3'] = generated_images[3] if len(generated_images) > 3 else ""
            # Store for mapping
            extracted_data['generated_image_urls'] = generated_images
        
        print(f"✅ Generated {len(generated_images)} Flipkart-compliant images")
        
        # Step 5: Validate Flipkart compliance
        print("🔍 Validating Flipkart marketplace compliance...")
        
        validation_prompt = f"""
        Validate this Flipkart marketplace listing:
        
        Product Category: {category}
        Generated Data Fields: {len(extracted_data)}
        Key Required Fields: Brand, Model Name, Description, MRP (INR), Search Keywords
        Image URLs Generated: {len(generated_images)}
        
        Sample Data:
        - Brand: {extracted_data.get('Brand', 'MISSING')}
        - Model Name: {extracted_data.get('Model Name', 'MISSING')}
        - Description Length: {len(str(extracted_data.get('Description', ''))) if extracted_data.get('Description') else 0} chars
        - MRP: {extracted_data.get('MRP (INR)', 'MISSING')}
        - Images: {len(generated_images)} generated
        
        Check for:
        1. Required field completeness (Brand, Model Name, Description, Pricing)
        2. Character limits compliance (Description 500-2000 chars)
        3. SEO optimization (Keywords, Features)
        4. Image requirements (1-7 images, 200x800+ resolution)
        5. Data quality and realism
        """
        
        validator_team = RoundRobinGroupChat([validation_agent], termination_condition=MaxMessageTermination(2))
        validation_result = await validator_team.run(task=validation_prompt)
        
        validation_content = str(validation_result.messages[-1].content)
        print(f"📋 Validation result: {validation_content[:200]}...")
        
        # Step 6: Save to Excel with proper data mapping
        print("💾 Saving to Flipkart Excel format...")
        
        # Add final data quality metrics
        total_flipkart_fields = len(flipkart_columns)
        populated_fields = len([k for k, v in extracted_data.items() if v and k in flipkart_columns])
        data_quality = (populated_fields / total_flipkart_fields) * 100 if total_flipkart_fields > 0 else 0
        
        print(f"📊 Data completeness: {populated_fields}/{total_flipkart_fields} fields ({data_quality:.1f}%)")
        
        success = processor.add_new_row(target_sheet, extracted_data)
        
        return {
            "status": "completed" if success else "failed",
            "category": category,
            "demographic": demographic,
            "generated_images": generated_images,
            "flipkart_data": extracted_data,
            "excel_updated": success,
            "data_quality_metrics": {
                "total_flipkart_fields": total_flipkart_fields,
                "populated_fields": populated_fields,
                "completion_percentage": round(data_quality, 1),
                "key_fields_status": {
                    "Brand": "✅" if extracted_data.get('Brand') else "❌",
                    "Model Name": "✅" if extracted_data.get('Model Name') else "❌", 
                    "Description": f"✅ ({len(str(extracted_data.get('Description', '')))} chars)" if extracted_data.get('Description') else "❌",
                    "MRP (INR)": "✅" if extracted_data.get('MRP (INR)') else "❌",
                    "Search Keywords": "✅" if extracted_data.get('Search Keywords') else "❌"
                }
            },
            "flipkart_compliance": {
                "images_generated": len(generated_images),
                "images_compliant": 1 <= len(generated_images) <= 7,
                "required_fields_filled": populated_fields >= 10,  # Minimum viable listing
                "seo_optimized": bool(extracted_data.get('Search Keywords') and extracted_data.get('Key Features'))
            }
        }

# Test functions
def setup_test_environment():
    """Setup test environment"""
    required_env_vars = ["OPENAI_API_KEY", "REPLICATE_API_TOKEN"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    os.makedirs("test_images", exist_ok=True)
    os.makedirs("excel_files", exist_ok=True)
    
    print("✅ Environment ready")
    return True

async def test_system():
    """Test the fixed system"""
    
    if not setup_test_environment():
        return
    
    # Initialize system
    system = ProductListingSystem(
        shoe_excel_path="excel_files/shoes_data.xlsx",
        jewellery_excel_path="excel_files/jewellery_data.xlsx"
    )
    
    # Get test input
    print("📥 Loading test data...")
    images, product_text = InputHandler.create_test_input()
    
    print(f"📊 Input: {len(images)} images, text: '{product_text[:100]}...'")
    
    # Process the product
    try:
        result = await system.process_product(images, product_text)
        
        print("\n🎉 FLIPKART LISTING COMPLETED!")
        print("=" * 60)
        print(f"Status: {result['status']}")
        print(f"Category: {result['category']}")
        print(f"Demographic: {result['demographic']}")
        print(f"Images Generated: {len(result['generated_images'])}")
        print(f"Excel Updated: {result['excel_updated']}")
        
        # Data Quality Metrics
        metrics = result['data_quality_metrics']
        print(f"\n📊 DATA QUALITY METRICS:")
        print(f"   Completion: {metrics['completion_percentage']}% ({metrics['populated_fields']}/{metrics['total_flipkart_fields']} fields)")
        print(f"   Key Fields Status:")
        for field, status in metrics['key_fields_status'].items():
            print(f"      {field}: {status}")
        
        # Flipkart Compliance
        compliance = result['flipkart_compliance']
        print(f"\n✅ FLIPKART COMPLIANCE:")
        print(f"   Images: {compliance['images_generated']}/7 (Compliant: {compliance['images_compliant']})")
        print(f"   Required Fields: {'✅' if compliance['required_fields_filled'] else '❌'}")
        print(f"   SEO Optimized: {'✅' if compliance['seo_optimized'] else '❌'}")
        
        # Sample generated data
        sample_data = result['flipkart_data']
        print(f"\n📝 SAMPLE GENERATED DATA:")
        print(f"   Brand: {sample_data.get('Brand', 'N/A')}")
        print(f"   Model: {sample_data.get('Model Name', 'N/A')}")
        print(f"   Price: MRP ₹{sample_data.get('MRP (INR)', 'N/A')} / Selling ₹{sample_data.get('Your selling price (INR)', 'N/A')}")
        print(f"   Description: {(sample_data.get('Description', 'N/A'))[:100]}...")
        print(f"   Keywords: {sample_data.get('Search Keywords', 'N/A')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Fixed Multi-Agent Product Listing System")
    print("Testing with proper reference images and CSV mapping...")
    asyncio.run(test_system())