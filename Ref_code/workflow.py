import os
import pandas as pd
import base64
import glob
import json
from openai import OpenAI
import replicate
from datetime import datetime
import requests
from urllib.parse import urlparse

class ProductDataProcessor:
    def __init__(self, openai_api_key, replicate_api_key):
        self.openai_client = OpenAI(api_key=openai_api_key)
        os.environ["REPLICATE_API_TOKEN"] = replicate_api_key
        self.excel_data = {}
        self.guidelines = {}
        self.mandatory_fields = []
        self.optional_fields = []
        self.field_constraints = {}
        
    def read_excel_file(self, excel_path):
        """Read all sheets from Excel file and analyze structure"""
        try:
            # Handle both .xls and .xlsx files
            if excel_path.endswith('.xls'):
                all_sheets = pd.read_excel(excel_path, sheet_name=None, engine='xlrd')
            else:
                all_sheets = pd.read_excel(excel_path, sheet_name=None, engine='openpyxl')
            self.excel_data = all_sheets
            
            print(f"Successfully read Excel file with {len(all_sheets)} sheets:")
            for sheet_name in all_sheets.keys():
                print(f"  - {sheet_name}: {all_sheets[sheet_name].shape}")
            
            # Process different sheets
            self._process_constraint_sheets()
            self._process_guidelines_sheet()
            
            return True
            
        except Exception as e:
            print(f"Error reading Excel file: {str(e)}")
            return False
    
    def _process_constraint_sheets(self):
        """Process sheets containing field constraints and mandatory/optional indicators"""
        # Look for sheets that might contain field constraints
        constraint_sheets = [name for name in self.excel_data.keys() 
                           if any(keyword in name.lower() for keyword in 
                                ['constraint', 'rule', 'mandatory', 'optional', 'field'])]
        
        for sheet_name in constraint_sheets:
            df = self.excel_data[sheet_name]
            print(f"Processing constraint sheet: {sheet_name}")
            
            # Look for color coding or mandatory/optional indicators
            for col in df.columns:
                if 'mandatory' in col.lower() or 'required' in col.lower():
                    mandatory_fields = df[col].dropna().tolist()
                    self.mandatory_fields.extend(mandatory_fields)
                elif 'optional' in col.lower():
                    optional_fields = df[col].dropna().tolist()
                    self.optional_fields.extend(optional_fields)
    
    def _process_guidelines_sheet(self):
        """Process the last sheet containing image guidelines"""
        sheet_names = list(self.excel_data.keys())
        if sheet_names:
            guidelines_sheet = sheet_names[-1]  # Last sheet
            df = self.excel_data[guidelines_sheet]
            
            print(f"Processing guidelines sheet: {guidelines_sheet}")
            
            # Extract meaningful guidelines text, skip empty/unnamed columns
            guidelines_text = ""
            for col in df.columns:
                if not col.startswith('Unnamed'):
                    col_data = df[col].dropna().astype(str).tolist()
                    if col_data and any(text.strip() for text in col_data):
                        guidelines_text += f"{col}: {' '.join(col_data)}\n"
            
            # If no meaningful data found, create basic guidelines
            if not guidelines_text.strip():
                guidelines_text = "Professional product photography with natural lighting, clean background, focus on product details and color accuracy."
            
            self.guidelines = {
                'image_guidelines': guidelines_text,
                'sheet_name': guidelines_sheet
            }
    
    def encode_image_to_base64(self, image_path):
        """Convert image to base64 string"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def get_image_mime_type(self, image_path):
        """Get the MIME type of the image"""
        extension = os.path.splitext(image_path)[1].lower()
        mime_types = {
            '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', 
            '.png': 'image/png', '.gif': 'image/gif', '.webp': 'image/webp'
        }
        return mime_types.get(extension, 'image/jpeg')
    
    def analyze_product_with_openai(self, image_directory, product_description):
        """Analyze product images and generate comprehensive product data"""
        
        # Get all images
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']
        image_paths = []
        for extension in image_extensions:
            image_paths.extend(glob.glob(os.path.join(image_directory, extension)))
            image_paths.extend(glob.glob(os.path.join(image_directory, extension.upper())))
        
        if not image_paths:
            raise ValueError("No images found in the specified directory")
        
        print(f"Found {len(image_paths)} images for analysis")
        
        # Prepare the comprehensive prompt
        prompt = self._generate_analysis_prompt(product_description)
        
        # Prepare message content
        message_content = [{"type": "text", "text": prompt}]
        
        # Add images to the message
        for image_path in image_paths:
            try:
                base64_image = self.encode_image_to_base64(image_path)
                mime_type = self.get_image_mime_type(image_path)
                
                message_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{base64_image}"
                    }
                })
            except Exception as e:
                print(f"Error processing image {image_path}: {str(e)}")
                continue
        
        # Send request to OpenAI
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": message_content
                }],
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Error calling OpenAI API: {str(e)}")
    
    def _generate_analysis_prompt(self, product_description):
        """Generate comprehensive prompt for product analysis"""
        
        # Get the product data sheet (3rd sheet)
        sheet_names = list(self.excel_data.keys())
        if len(sheet_names) >= 3:
            product_sheet = self.excel_data[sheet_names[2]]
            columns = product_sheet.columns.tolist()
        else:
            columns = ["Brand", "Article Number", "Size", "Color", "Style Code", 
                      "Ideal For", "Occasion", "Outer Material", "Heel Height", 
                      "Description", "Key Features"]
        
        prompt = f"""
You are an expert e-commerce product data analyst. Analyze the provided product images and description to generate comprehensive product data.

**PRODUCT DESCRIPTION PROVIDED:**
{product_description}

**EXCEL STRUCTURE ANALYSIS:**
I have an Excel file with multiple sheets containing:
- Field constraints and validation rules
- Mandatory vs optional field indicators  
- Image guidelines for product photography

**YOUR TASK:**
Based on the images and description, generate accurate data for these specific columns:
{', '.join(columns)}

**ANALYSIS REQUIREMENTS:**

1. **PRODUCT IDENTIFICATION:**
   - Determine exact product type, category, and subcategory
   - Identify brand if visible or inferable
   - Generate appropriate article/model number if not provided

2. **PHYSICAL SPECIFICATIONS:**
   - Size and measurements (length, breadth, height, weight)
   - Material composition (outer material, sole material, inner material)
   - Color analysis (primary and secondary colors)
   - Style and design elements

3. **TECHNICAL DETAILS:**
   - HSN code for the product category
   - Heel height measurements (if applicable)
   - Closure type, tip shape, heel pattern
   - Pack specifications

4. **MARKETPLACE DATA:**
   - Suggested MRP and selling price ranges
   - Ideal customer demographics (age, gender, usage)
   - Occasion suitability (casual, formal, sports, ethnic)
   - Search keywords and key features

5. **CONTENT GENERATION:**
   - Compelling product title
   - Detailed product description
   - Care instructions
   - Sales package contents

**MANDATORY FIELD COMPLIANCE:**
Based on the Excel constraints, prioritize filling mandatory fields first.
For optional fields, only fill if you have confident data.

**OUTPUT FORMAT:**
Provide the response as a structured JSON with:
```json
{{
  "product_data": {{
    "column_name": "value",
    ...
  }},
  "confidence_scores": {{
    "column_name": confidence_score_0_to_10,
    ...
  }},
  "suggestions": {{
    "column_name": "suggestion_for_missing_data",
    ...
  }},
  "image_analysis": {{
    "best_images_for_modeling": ["image1.jpg", "image2.jpg"],
    "image_quality_assessment": "detailed_assessment",
    "recommended_additional_angles": ["front_view", "side_view", "etc"]
  }}
}}
```

**CRITICAL REQUIREMENTS:**
- If uncertain about any data, use "confidence_scores" to indicate uncertainty
- For missing data, provide specific "suggestions" on how to obtain it
- Identify the 2 best images for AI modeling/generation purposes
- Ensure all measurements and specifications are realistic and accurate
- Follow e-commerce marketplace standards for descriptions and keywords

Analyze the images thoroughly and provide comprehensive, accurate product data.
"""
        return prompt
    
    def process_openai_response(self, response_text):
        """Process and parse OpenAI response"""
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                return json.loads(json_str)
            else:
                # Try to parse the entire response as JSON
                return json.loads(response_text)
        except json.JSONDecodeError:
            print("Warning: Could not parse JSON response. Using text analysis.")
            return {"raw_response": response_text}
    
    def generate_replicate_prompt(self, product_data, image_analysis):
        """Generate minimal prompt for Replicate model based on reference images"""
        
        # Extract basic info
        ideal_for = product_data.get('Ideal For', 'women')
        occasion = product_data.get('Occasion', 'casual')
        
        # Keep it minimal and reference-focused
        replicate_prompt = f"""
A {ideal_for} model wearing the exact shoes from the reference images in a modern {occasion} setting. 

CRITICAL: Follow the reference images exactly for:
- Shoe color, material, and design
- All hardware details (laces, eyelets, sole)
- Proportions and shape

Show the person wearing these shoes naturally in an urban environment with good lighting that preserves the original shoe appearance.
"""
        
        return replicate_prompt
    
    def select_best_images(self, image_directory, image_analysis):
        """Select the best 2 images based on AI analysis"""
        
        # Get all images
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']
        image_paths = []
        for extension in image_extensions:
            image_paths.extend(glob.glob(os.path.join(image_directory, extension)))
            image_paths.extend(glob.glob(os.path.join(image_directory, extension.upper())))
        
        # If AI provided specific recommendations, use those
        if 'best_images_for_modeling' in image_analysis:
            recommended_names = image_analysis['best_images_for_modeling']
            selected_images = []
            
            for rec_name in recommended_names[:2]:  # Take first 2
                for path in image_paths:
                    if rec_name in os.path.basename(path):
                        selected_images.append(path)
                        break
            
            if len(selected_images) >= 2:
                return selected_images[:2]
        
        # Fallback: select first 2 images
        return image_paths[:2] if len(image_paths) >= 2 else image_paths
    
    def convert_image_to_data_url(self, image_path):
        """Convert image file to data URL format for Replicate"""
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            base64_encoded = base64.b64encode(image_data).decode('utf-8')
            
            extension = os.path.splitext(image_path)[1].lower()
            mime_types = {
                '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', 
                '.png': 'image/png', '.gif': 'image/gif', '.webp': 'image/webp'
            }
            mime_type = mime_types.get(extension, 'image/jpeg')
            
            return f"data:{mime_type};base64,{base64_encoded}"
    
    def generate_lifestyle_images_with_replicate(self, selected_images, replicate_prompt):
        """Generate lifestyle images using Replicate API"""
        
        if len(selected_images) < 2:
            raise ValueError("Need at least 2 images for Replicate processing")
        
        try:
            # Convert images to data URLs
            image1_data_url = self.convert_image_to_data_url(selected_images[0])
            image2_data_url = self.convert_image_to_data_url(selected_images[1])
            
            print(f"Generating lifestyle images with Replicate...")
            print(f"Using images: {[os.path.basename(img) for img in selected_images]}")
            
            # Use a model optimized for product photography with better reference adherence
            output = replicate.run(
            "flux-kontext-apps/multi-image-kontext-max",
            input={
                "input_image_1": image1_data_url,
                "input_image_2": image2_data_url,
                "prompt": replicate_prompt,
                # Add other parameters as needed for the specific model
                # You may need to adjust these based on model requirements
                "num_inference_steps": 40,
                "guidance_scale": 7.5,
                "num_outputs": 1,
                "aspect_ratio": "1:1",
                "output_format": "jpg",
                "output_quality": 100,
                "disable_safety_checker": True
            }
        )
            
            return output
            
        except Exception as e:
            print(f"Error with primary model, trying alternative...")
            
            # Fallback to alternative model
            try:
                output = replicate.run(
                    "stability-ai/sdxl",
                    input={
                        "image": image1_data_url,
                        "prompt": replicate_prompt,
                        "strength": 0.7,
                        "num_inference_steps": 50,
                        "guidance_scale": 8.0,
                        "num_outputs": 2
                    }
                )
                return output
            except Exception as e2:
                raise Exception(f"Error calling Replicate API: {str(e2)}")
    
    def save_generated_images(self, output, save_directory="./generated_lifestyle_images"):
        """Save generated images from Replicate"""
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
        
        saved_paths = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if isinstance(output, list):
            for i, image_url in enumerate(output):
                try:
                    response = requests.get(image_url)
                    if response.status_code == 200:
                        filename = f"lifestyle_image_{timestamp}_{i+1}.webp"
                        image_path = os.path.join(save_directory, filename)
                        
                        with open(image_path, "wb") as f:
                            f.write(response.content)
                        
                        saved_paths.append(image_path)
                        print(f"Saved: {image_path}")
                except Exception as e:
                    print(f"Error saving image {i+1}: {str(e)}")
        else:
            try:
                response = requests.get(output)
                if response.status_code == 200:
                    filename = f"lifestyle_image_{timestamp}.webp"
                    image_path = os.path.join(save_directory, filename)
                    
                    with open(image_path, "wb") as f:
                        f.write(response.content)
                    
                    saved_paths.append(image_path)
                    print(f"Saved: {image_path}")
            except Exception as e:
                print(f"Error saving image: {str(e)}")
        
        return saved_paths
    
    def save_product_data_to_excel(self, product_data, output_path):
        """Save generated product data back to Excel"""
        try:
            sheet_names = list(self.excel_data.keys())
            print(f"Original sheets found: {sheet_names}")
            
            if len(sheet_names) >= 3:
                target_sheet = sheet_names[2]
                print(f"Target sheet for product data: {target_sheet}")
                
                # Create a copy of the target sheet
                df = self.excel_data[target_sheet].copy()
                
                # Add new row with generated data
                new_row = {}
                for col in df.columns:
                    if col in product_data:
                        new_row[col] = product_data[col]
                    else:
                        new_row[col] = ""
                
                # Append the new row
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                
                # Ensure output path ends with .xlsx for better compatibility
                if not output_path.endswith('.xlsx'):
                    output_path = output_path.replace('.xls', '.xlsx')
                
                # Remove existing file if it exists
                if os.path.exists(output_path):
                    try:
                        os.remove(output_path)
                        print(f"Removed existing file: {output_path}")
                    except Exception as e:
                        print(f"Warning: Could not remove existing file: {e}")
                        # Try with a timestamp suffix if we can't remove
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        base_path = output_path.replace('.xlsx', '')
                        output_path = f"{base_path}_{timestamp}.xlsx"
                        print(f"Using alternative path: {output_path}")
                
                # Save to new Excel file
                with pd.ExcelWriter(output_path, engine='openpyxl', mode='w') as writer:
                    # Write all original sheets first
                    for sheet_name, sheet_df in self.excel_data.items():
                        try:
                            if sheet_name == target_sheet:
                                # Write updated target sheet with new product data
                                df.to_excel(writer, sheet_name=sheet_name, index=False)
                                print(f"Updated sheet '{sheet_name}' with product data")
                            else:
                                # Write original sheets as-is
                                sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
                                print(f"Preserved original sheet: '{sheet_name}'")
                        except Exception as sheet_error:
                            print(f"Warning: Could not save sheet '{sheet_name}': {str(sheet_error)}")
                            continue
                
                print(f"All sheets saved to: {output_path}")
                print(f"Total sheets in output: {len(self.excel_data)}")
                
                # Verify the file was created
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    print(f"File successfully created: {output_path} ({file_size} bytes)")
                    return True
                else:
                    print(f"Error: File was not created at {output_path}")
                    return False
            else:
                print(f"Error: Need at least 3 sheets, found only {len(sheet_names)}")
                return False
                
        except Exception as e:
            print(f"Error saving to Excel: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def process_complete_workflow(self, excel_path, image_directory, product_description, output_dir="./output"):
        """Complete workflow: Excel analysis -> Product data generation -> Lifestyle image creation"""
        
        try:
            # Step 1: Read and analyze Excel
            print("Step 1: Reading Excel file...")
            if not self.read_excel_file(excel_path):
                return False
            
            # Step 2: Analyze product with OpenAI
            print("\nStep 2: Analyzing product with OpenAI...")
            openai_response = self.analyze_product_with_openai(image_directory, product_description)
            
            # Step 3: Process OpenAI response
            print("\nStep 3: Processing OpenAI response...")
            parsed_data = self.process_openai_response(openai_response)
            
            if 'product_data' not in parsed_data:
                print("Warning: Could not extract structured product data")
                parsed_data = {'product_data': {}, 'image_analysis': {}}
            
            product_data = parsed_data.get('product_data', {})
            image_analysis = parsed_data.get('image_analysis', {})
            
            # Step 4: Generate Replicate prompt
            print("\nStep 4: Generating Replicate prompt...")
            replicate_prompt = self.generate_replicate_prompt(product_data, image_analysis)
            
            # Step 5: Select best images
            print("\nStep 5: Selecting best images...")
            selected_images = self.select_best_images(image_directory, image_analysis)
            
            # Step 6: Generate lifestyle images
            print("\nStep 6: Generating lifestyle images with Replicate...")
            replicate_output = self.generate_lifestyle_images_with_replicate(selected_images, replicate_prompt)
            
            # Step 7: Save everything
            print("\nStep 7: Saving results...")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Save generated images
            saved_image_paths = self.save_generated_images(
                replicate_output, 
                os.path.join(output_dir, "lifestyle_images")
            )
            
            # Save product data to Excel with timestamp to avoid conflicts
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_excel_path = os.path.join(output_dir, f"updated_product_data_{timestamp}.xlsx")
            excel_saved = self.save_product_data_to_excel(product_data, output_excel_path)
            
            # If Excel save failed, try alternative method
            if not excel_saved:
                print("Primary Excel save failed, trying alternative method...")
                alt_path = os.path.join(output_dir, f"product_data_backup_{timestamp}.csv")
                try:
                    # Save as CSV as fallback
                    sheet_names = list(self.excel_data.keys())
                    if len(sheet_names) >= 3:
                        target_sheet = sheet_names[2]
                        df = self.excel_data[target_sheet].copy()
                        new_row = pd.DataFrame([product_data])
                        df = pd.concat([df, new_row], ignore_index=True)
                        df.to_csv(alt_path, index=False)
                        print(f"Product data saved as CSV backup: {alt_path}")
                except Exception as csv_error:
                    print(f"CSV backup also failed: {csv_error}")
            
            # Save analysis report with Excel verification
            report = {
                'timestamp': datetime.now().isoformat(),
                'input_description': product_description,
                'excel_info': {
                    'input_file': excel_path,
                    'total_sheets': len(self.excel_data),
                    'sheet_names': list(self.excel_data.keys()),
                    'target_sheet': list(self.excel_data.keys())[2] if len(self.excel_data) >= 3 else None
                },
                'openai_analysis': openai_response,
                'parsed_product_data': product_data,
                'confidence_scores': parsed_data.get('confidence_scores', {}),
                'suggestions': parsed_data.get('suggestions', {}),
                'replicate_prompt': replicate_prompt,
                'selected_images': [os.path.basename(img) for img in selected_images],
                'generated_image_paths': saved_image_paths
            }
            
            report_path = os.path.join(output_dir, "analysis_report.json")
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"\n{'='*60}")
            print("WORKFLOW COMPLETED SUCCESSFULLY!")
            print(f"{'='*60}")
            print(f"Output directory: {output_dir}")
            print(f"Generated lifestyle images: {len(saved_image_paths)}")
            print(f"Product data saved to: {output_excel_path}")
            print(f"Analysis report: {report_path}")
            
            return True
            
        except Exception as e:
            print(f"Error in workflow: {str(e)}")
            return False

# Example usage
# if __name__ == "__main__":
#     # Configuration
#     EXCEL_PATH = "/home/nawnit08k/listing_generator/input_excel/C_shoe_c891f166a1f44b25.xls"
#     IMAGE_DIRECTORY = "/home/nawnit08k/listing_generator/test_images/shoes/shoe2" 
#     OPENAI_API_KEY = "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"      # Update with your API key
#     REPLICATE_API_KEY = "r8_Nqq9h7dHI3bTviOfEge3HmrLNPUcoQS23et0O" 
#     OUTPUT_DIRECTORY = "./product_output"
    
#     # Product description (rough text about the product)
#     PRODUCT_DESCRIPTION = """
#     Black ankle boots for women. Suede material with lace-up design. 
#     Chunky heel and platform sole. Suitable for casual wear.
#     Gold eyelets and black laces. Urban style footwear.
#     """
    
#     # Initialize processor
#     processor = ProductDataProcessor(
#         openai_api_key=OPENAI_API_KEY,
#         replicate_api_key=REPLICATE_API_KEY
#     )
    
#     # Run complete workflow
#     success = processor.process_complete_workflow(
#         excel_path=EXCEL_PATH,
#         image_directory=IMAGE_DIRECTORY,
#         product_description=PRODUCT_DESCRIPTION,
#         output_dir=OUTPUT_DIRECTORY
#     )
    
#     if success:
#         print("Product processing completed successfully!")
#     else:
#         print("Product processing failed. Check the logs for details.")