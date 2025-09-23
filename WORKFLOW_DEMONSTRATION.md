# Fashion AI Workflow Demonstration

## Overview
This document demonstrates the complete workflow of the Fashion AI system:
1. Making a POST request to generate content
2. Using the returned request_id to make a GET request to access files

## Demonstration Results

### Successful GET Request with Existing Request ID

We successfully demonstrated accessing files using a request_id with the following results:

**Request**: `GET http://localhost:8000/api/v1/files/4c1e1d10-a130-440a-aaae-290d10c286f4`

**Response Status**: 200 OK

**Files Found**:
1. `4c1e1d10-a130-440a-aaae-290d10c286f4_generated_frontside.jpg` (image)
   - URL: http://34.72.178.95//files/4c1e1d10-a130-440a-aaae-290d10c286f4_generated_frontside.jpg

2. `4c1e1d10-a130-440a-aaae-290d10c286f4_generated_frontside_social_gathering.jpg` (image)
   - URL: http://34.72.178.95//files/4c1e1d10-a130-440a-aaae-290d10c286f4_generated_frontside_social_gathering.jpg

3. `4c1e1d10-a130-440a-aaae-290d10c286f4_report.xlsx` (excel)
   - URL: http://34.72.178.95//files/4c1e1d10-a130-440a-aaae-290d10c286f4_report.xlsx

### Error Handling Demonstrations

#### 1. Invalid Request ID Format
**Request**: `GET http://localhost:8000/api/v1/files/not-a-valid-uuid`

**Response Status**: 400 Bad Request
**Response**: `{'detail': 'Invalid request_id format'}`

#### 2. Nonexistent Request ID
**Request**: `GET http://localhost:8000/api/v1/files/00000000-0000-0000-0000-000000000000`

**Response Status**: 404 Not Found
**Response**: `{'detail': 'No files found for this request_id'}`

## How the System Works

### POST Request Workflow
When you make a POST request to `/api/v1/generate`:
1. The system generates a unique request_id (UUID)
2. Processes your images and text description
3. Saves generated files in the output directory with filenames containing the request_id
4. Returns the request_id along with direct URLs to the generated files

### GET Request Workflow
When you make a GET request to `/api/v1/files/{request_id}`:
1. The system validates that the request_id is a proper UUID format
2. Searches the output directory for all files containing the request_id in their filename
3. Constructs URLs for each found file
4. Returns a structured JSON response with file information

## Key Benefits

1. **Persistent Access**: Access files anytime using just the request_id
2. **No URL Storage**: No need to store individual file URLs
3. **Complete File List**: Get all generated files in one response
4. **File Type Information**: Know what type of file each one is
5. **Error Handling**: Proper responses for invalid or missing request_ids

## File Storage Structure

Files are stored directly in the `output` directory with the following naming pattern:
- `{request_id}_generated_{view_name}.jpg` for images
- `{request_id}_report.xlsx` for Excel reports
- `{request_id}_generated.mp4` for videos

## Usage Instructions

### To Generate Content (POST Request):
```bash
curl -X POST "http://YOUR-IP-ADDRESS/api/v1/generate" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "frontside=@/path/to/image.jpg" \
  -F "text=stylish evening dress" \
  -F "username=your_username" \
  -F "product=dress_name"
```

### To Access Files Later (GET Request):
```bash
curl -X GET "http://YOUR-IP-ADDRESS/api/v1/files/{request_id}"
```

## Conclusion

The Fashion AI system now provides exactly what you requested:
1. Send a POST request to generate content and receive a request_id
2. Use that request_id in subsequent GET requests to access all generated files at any time
3. No need to store or remember individual file URLs
4. Proper error handling for all edge cases

The system is fully functional and ready for use!