# Postman Collection for FashionModelingAI

This directory contains a Postman collection and environment configuration for testing the FashionModelingAI API.

## Prerequisites

1. [Postman](https://www.postman.com/downloads/) installed
2. The FashionModelingAI application running locally

## Setup Instructions

1. **Start the Application**
   Make sure the FashionModelingAI application is running on your local machine:
   ```
   cd c:\Users\LENOVO\Desktop\fashion\FashionModelingAI-master
   python -m uvicorn app.main:app --reload
   ```

2. **Import the Collection**
   - Open Postman
   - Click on "Import" in the top left corner
   - Select the `FashionModelingAI_Collection.json` file
   - Click "Import"

3. **Import the Environment**
   - In Postman, click on "Import" again
   - Select the `FashionModelingAI_Environment.json` file
   - Click "Import"
   - Select "FashionModelingAI Local" from the environment dropdown in the top right

## API Endpoints

### 1. Health Check
- **Method**: GET
- **URL**: `{{base_url}}/`
- **Description**: Check if the API is running

### 2. Generate Fashion Content (Front + Detail)
- **Method**: POST
- **URL**: `{{base_url}}/api/v1/generate`
- **Description**: Generate fashion content from front and detail view images
- **Form Data**:
  - `frontside` (required): Front view image file
  - `detailview` (required): Detail view image file
  - `text` (required): Text description of desired output
  - `username` (required): User identifier for SKU generation
  - `product` (required): Product type for SKU generation
  - `generate_video` (optional): Boolean flag for video generation (true/false)
  - `numberOfOutputs` (optional): Number of image outputs to generate (1-4)
  - `aspectRatio` (optional): Aspect ratio for generated images (default: "9:16")

### 3. Generate Fashion Content (All Views)
- **Method**: POST
- **URL**: `{{base_url}}/api/v1/generate`
- **Description**: Generate fashion content from all available view images
- **Form Data**:
  - `frontside` (required): Front view image file
  - `backside` (optional): Back view image file
  - `sideview` (optional): Side view image file
  - `detailview` (optional): Detail view image file
  - `text` (required): Text description of desired output
  - `username` (required): User identifier for SKU generation
  - `product` (required): Product type for SKU generation
  - `generate_video` (optional): Boolean flag for video generation (true/false)
  - `numberOfOutputs` (optional): Number of image outputs to generate (1-4)
  - `aspectRatio` (optional): Aspect ratio for generated images (default: "9:16")

### 4. Generate Fashion Content (1:1 Aspect Ratio)
- **Method**: POST
- **URL**: `{{base_url}}/api/v1/generate`
- **Description**: Generate fashion content with square aspect ratio
- **Form Data**:
  - `frontside` (required): Front view image file
  - `detailview` (required): Detail view image file
  - `text` (required): Text description of desired output
  - `username` (required): User identifier for SKU generation
  - `product` (required): Product type for SKU generation
  - `generate_video` (optional): Boolean flag for video generation (true/false)
  - `numberOfOutputs` (optional): Number of image outputs to generate (1-4)
  - `aspectRatio` (optional): Aspect ratio set to "1:1" for square images

## Supported Aspect Ratios

The following aspect ratios are supported:
- `1:1` - Square images (equal width and height)
- `16:9` - Landscape orientation (wide screen)
- `4:3` - Landscape orientation (standard photo)
- `3:4` - Portrait orientation (standard photo)
- `9:16` - Portrait orientation (mobile phone style) - DEFAULT

## Example Usage

1. Select one of the "Generate Fashion Content" requests
2. In the "Body" tab, select "form-data"
3. For each file field, click "Select Files" and choose the appropriate image files:
   - For basic test: Select `ref1.jpg` for frontside and `usp1.jpg` for detailview
4. Fill in the required text fields:
   - text: "woman dress, stylish, elegant, event wear"
   - username: "test_user"
   - product: "dress"
5. Optionally change the `aspectRatio` field to one of the supported values
6. Click "Send" to make the request

## Expected Response

A successful response will include:
- `request_id`: Unique identifier for the request
- `output_image_url`: URL to the generated primary image
- `image_variations`: Array of URLs to additional image variations
- `output_video_url`: URL to the generated video (if requested)
- `excel_report_url`: URL to the generated Excel report
- `metadata`: Additional information about the generation process

## Understanding Parameters

### numberOfOutputs
The `numberOfOutputs` parameter controls how many lifestyle variations are generated:
- Even with `numberOfOutputs=1`, you'll get at least one lifestyle variation
- The primary image (studio view) is always generated
- Additional variations are lifestyle images with different backgrounds/occasions

### aspectRatio
The `aspectRatio` parameter controls the dimensions of the generated images:
- Default value is `9:16` (portrait orientation, height 1.78x width)
- All generated images will use the specified aspect ratio
- Choose based on your intended use (social media, e-commerce, etc.)

## Troubleshooting

1. **Connection Refused**: Make sure the application is running on localhost:8000
2. **File Upload Issues**: Ensure image files are in the correct format (JPEG/PNG)
3. **API Key Errors**: Make sure all required environment variables are set in your .env file
4. **Image Not Found**: Verify that test images exist in the `tests/test_data` directory
5. **Invalid Aspect Ratio**: Make sure the aspectRatio value is one of the supported options