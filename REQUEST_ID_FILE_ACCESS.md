# File Access System Using Request ID

## Overview
This document describes how to access generated files using GET requests with the request_id. The system allows you to send a POST request to generate content, receive a request_id, and then use that request_id in subsequent GET requests to access the generated files at any time.

## How It Works

### 1. POST Request - Content Generation
When you send a POST request to `/api/v1/generate`, the system:
1. Generates a unique `request_id` (UUID)
2. Processes your images and text description
3. Saves all generated files with filenames that include the request_id
4. Returns a response with the request_id and direct URLs to the files

### 2. GET Request - File Access
You can later access all files associated with a request_id by sending a GET request to:
```
GET /api/v1/files/{request_id}
```

This returns a JSON response with all files associated with that request_id.

## API Endpoints

### POST /api/v1/generate
Generates fashion content from images and text description.

**Request:**
```bash
curl -X POST "http://YOUR-IP-ADDRESS/api/v1/generate" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "frontside=@/path/to/image.jpg" \
  -F "text=woman dress, stylish, elegant, event wear" \
  -F "username=test_user" \
  -F "product=dress"
```

**Response:**
```json
{
  "request_id": "123e4567-e89b-12d3-a456-426614174000",
  "output_image_url": "http://YOUR-IP-ADDRESS/files/123e4567-e89b-12d3-a456-426614174000_generated_frontside.jpg",
  "image_variations": [
    "http://YOUR-IP-ADDRESS/files/123e4567-e89b-12d3-a456-426614174000_generated_frontside_social_gathering.jpg"
  ],
  "output_video_url": null,
  "excel_report_url": "http://YOUR-IP-ADDRESS/files/123e4567-e89b-12d3-a456-426614174000_report.xlsx",
  "metadata": {}
}
```

### GET /api/v1/files/{request_id}
Retrieves all files associated with a specific request_id.

**Request:**
```bash
curl -X GET "http://YOUR-IP-ADDRESS/api/v1/files/123e4567-e89b-12d3-a456-426614174000"
```

**Response:**
```json
{
  "request_id": "123e4567-e89b-12d3-a456-426614174000",
  "files": [
    {
      "filename": "123e4567-e89b-12d3-a456-426614174000_generated_frontside.jpg",
      "url": "http://YOUR-IP-ADDRESS/files/123e4567-e89b-12d3-a456-426614174000_generated_frontside.jpg",
      "type": "image"
    },
    {
      "filename": "123e4567-e89b-12d3-a456-426614174000_generated_frontside_social_gathering.jpg",
      "url": "http://YOUR-IP-ADDRESS/files/123e4567-e89b-12d3-a456-426614174000_generated_frontside_social_gathering.jpg",
      "type": "image"
    },
    {
      "filename": "123e4567-e89b-12d3-a456-426614174000_report.xlsx",
      "url": "http://YOUR-IP-ADDRESS/files/123e4567-e89b-12d3-a456-426614174000_report.xlsx",
      "type": "excel"
    }
  ],
  "count": 3
}
```

## File Storage Structure

Files are stored in the `output` directory with the following naming convention:
- Images: `{request_id}_generated_{view_name}.jpg`
- Excel reports: `{request_id}_report.xlsx`
- Videos: `{request_id}_generated.mp4`

The system uses the request_id to identify and retrieve all related files.

## Implementation Details

### File Access Endpoint
The GET endpoint `/api/v1/files/{request_id}` works by:
1. Validating the request_id format (must be a valid UUID)
2. Searching the output directory for all files containing the request_id in their filename
3. Constructing URLs for each file using the static file server
4. Returning a structured response with file information

### File Type Detection
The system automatically detects file types based on extensions:
- Images: .jpg, .jpeg, .png, .gif
- Videos: .mp4, .avi, .mov
- Excel: .xlsx, .xls
- PDF: .pdf
- Other: All other file types

## Usage Examples

### Example 1: Complete Workflow
1. Send POST request to generate content:
```bash
curl -X POST "http://YOUR-IP-ADDRESS/api/v1/generate" \
  -F "frontside=@/path/to/front.jpg" \
  -F "text=stylish dress for evening events" \
  -F "username=user123" \
  -F "product=evening_dress"
```

2. Receive response with request_id:
```json
{
  "request_id": "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8",
  "output_image_url": "...",
  ...
}
```

3. Later, retrieve all files using the request_id:
```bash
curl -X GET "http://YOUR-IP-ADDRESS/api/v1/files/a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8"
```

### Example 2: Error Handling
If you provide an invalid request_id:
```bash
curl -X GET "http://YOUR-IP-ADDRESS/api/v1/files/invalid-request-id"
```
Response: 400 Bad Request

If no files exist for a valid request_id:
```bash
curl -X GET "http://YOUR-IP-ADDRESS/api/v1/files/00000000-0000-0000-0000-000000000000"
```
Response: 404 Not Found

## Benefits

1. **Persistent Access**: Access files anytime using just the request_id
2. **No URL Storage Needed**: You don't need to store individual file URLs
3. **Complete File List**: Get all generated files in one response
4. **File Type Information**: Know what type of file each one is
5. **Error Handling**: Proper error responses for invalid or missing request_ids

## Troubleshooting

### Common Issues

1. **404 Not Found**: No files exist for the provided request_id
   - Solution: Verify the request_id is correct and files were generated

2. **400 Bad Request**: Invalid request_id format
   - Solution: Ensure the request_id is a valid UUID

3. **500 Internal Server Error**: Server-side issue
   - Solution: Check server logs for details

### File Access Issues

If files are not accessible through the URLs:
1. Ensure the static file server is running correctly
2. Verify the LOCAL_BASE_URL setting in your configuration
3. Check file permissions on the output directory

## Security Considerations

1. **Request ID Validation**: All request_ids are validated as UUID format
2. **File Path Security**: The system only accesses files in the designated output directory
3. **No Directory Traversal**: Filenames are not used directly in file paths
4. **Access Control**: Consider adding authentication for production use

## Testing

You can test the implementation using the provided test scripts or with curl/postman:

1. Make a POST request to generate content
2. Note the request_id from the response
3. Make a GET request to `/api/v1/files/{request_id}` to retrieve all files
4. Verify that all expected files are returned with correct URLs

The system has been tested with various request_ids and file types to ensure reliability.