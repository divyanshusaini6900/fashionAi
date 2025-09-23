# numberOfOutputs Feature Implementation

## 📋 Feature Overview
Added `numberOfOutputs` parameter to the Fashion AI API that allows users to request multiple image outputs in a single API call.

## 🔧 Implementation Details

### 1. API Endpoint Changes
- Added `numberOfOutputs` parameter to `/api/v1/generate` endpoint
- Parameter type: integer (1-4)
- Default value: 1
- Validation: minimum 1, maximum 4

### 2. Updated Files

#### `/app/api/v1/endpoints/generate.py`
- Added `numberOfOutputs` form parameter with validation
- Updated workflow manager call to pass the parameter

#### `/app/services/workflow_manager.py`
- Updated `process_request` method to accept `number_of_outputs` parameter
- Passed parameter to image generator

#### `/app/services/image_generator.py`
- Updated `generate_images` method to support multiple outputs
- Enhanced occasion/background generation to create requested number of variations
- Added support for 6 different occasions: social_gathering, formal_event, casual_outing, party_venue, outdoor_setting, studio_portrait

#### `/openapi.json`
- Updated OpenAPI specification to include numberOfOutputs parameter
- Added proper validation constraints (1-4 range)

### 3. Feature Behavior

When `numberOfOutputs=1`: 
- Generates primary frontside image + 1 lifestyle variation

When `numberOfOutputs=2`:
- Generates primary frontside image + 2 lifestyle variations  

When `numberOfOutputs=3`:
- Generates primary frontside image + 3 lifestyle variations

When `numberOfOutputs=4`:
- Generates primary frontside image + 4 lifestyle variations

### 4. Response Structure
The API response maintains the same structure:
- `output_image_url`: Primary image (frontside)
- `image_variations`: Array of additional generated images
- Total images = 1 (primary) + numberOfOutputs variations

### 5. Test File
Created `test_number_of_outputs.py` to validate the feature works correctly with different values.

## 🎯 Usage Example

```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -F "text=woman dress, elegant, party wear" \
  -F "username=Mene" \
  -F "product=dress" \
  -F "numberOfOutputs=3" \
  -F "frontside=@image.jpg"
```

This will generate:
- 1 primary image (frontside view)
- 3 lifestyle variations with different backgrounds/occasions
- Total: 4 images

## ✅ Benefits
1. **Efficiency**: Generate multiple variations in one API call
2. **Variety**: Different backgrounds and occasions for marketing
3. **Flexibility**: Users can choose how many outputs they need
4. **Cost-effective**: Batch generation is more efficient than multiple calls

## 🔧 Configuration
The feature works with both Gemini and Replicate APIs:
- **Gemini**: Uses imagen-4.0-generate-001 model
- **Replicate**: Uses flux-kontext-apps/multi-image-kontext-max model
- Automatic fallback from Gemini to Replicate if quota exceeded

## 🚀 Ready to Use
The numberOfOutputs feature is now fully implemented and ready for testing!