# Background Array Feature Documentation

## Overview

The Background Array feature allows you to specify exactly how many images to generate with different background types for each view. This gives you fine-grained control over the image generation process.

## Background Array Format

Each view can have a background array with 3 integers: `[white_count, plain_count, random_count]`

- **white_count**: Number of images with clean white backgrounds
- **plain_count**: Number of images with plain (non-white) backgrounds
- **random_count**: Number of images with random lifestyle backgrounds

## Examples

### Example 1: Background Array [0, 0, 1] with numberOfOutputs = 1
- Generates 1 image with a random lifestyle background
- Total: 1 image

### Example 2: Background Array [0, 1, 1] with numberOfOutputs = 2
- Generates 1 image with a plain (non-white) background
- Generates 1 image with a random lifestyle background
- Total: 2 images

### Example 3: Background Array [1, 0, 1] with numberOfOutputs = 2
- Generates 1 image with a clean white background
- Generates 1 image with a random lifestyle background
- Total: 2 images

### Example 4: Background Array [2, 0, 0] with numberOfOutputs = 2
- Generates 2 images with clean white backgrounds
- Total: 2 images

### Example 5: Background Array [1, 1, 2] with numberOfOutputs = 4
- Generates 1 image with a clean white background
- Generates 1 image with a plain background
- Generates 2 images with random lifestyle backgrounds
- Total: 4 images

## API Endpoint

### New Endpoint
```
POST /api/v1/generate/image
```

### Request Format
```json
{
  "inputImages": [
    {
      "url": "https://example.com/front_view.jpg",
      "view": "front",
      "backgrounds": [1, 0, 0]
    }
  ],
  "productType": "general",
  "gender": "woman",
  "text": "Top",
  "isVideo": false,
  "upscale": true,
  "numberOfOutputs": 1,
  "generateCsv": true
}
```

### Response Format
```json
{
  "request_id": "123e4567-e89b-12d3-a456-426614174000",
  "output_image_url": "http://localhost:8000/files/generated/123e4567-e89b-12d3-a456-426614174000/output.jpg",
  "image_variations": [
    "http://localhost:8000/files/generated/123e4567-e89b-12d3-a456-426614174000/variation1.jpg"
  ],
  "output_video_url": null,
  "excel_report_url": "http://localhost:8000/files/generated/123e4567-e89b-12d3-a456-426614174000/report.xlsx",
  "metadata": {
    "processing_time": 45.2,
    "model_used": "stable-diffusion-v3"
  }
}
```

## Testing

To test the new feature, run:
```bash
python test_background_array.py
```

This will test the background array functionality with sample data.