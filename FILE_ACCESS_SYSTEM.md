# File Access System Using Request ID

## Overview
This document describes how to implement a system that allows you to access generated files using GET requests with the request_id.

## Current System Analysis

### How POST Request Works
1. Client sends POST request to `/api/v1/generate` with images and parameters
2. Server generates a unique `request_id` (UUID)
3. Files are processed and saved to the `output` directory with filenames that include the request_id:
   - Format: `{request_id}_generated_{view_name}.jpg` for images
   - Format: `{request_id}_report.xlsx` for Excel reports
   - Format: `{request_id}_generated.mp4` for videos
4. Response includes URLs to access the generated files:
   ```json
   {
     "request_id": "unique-request-id",
     "output_image_url": "http://YOUR-IP-ADDRESS/files/request-id_generated_frontside.jpg",
     "image_variations": [
       "http://YOUR-IP-ADDRESS/files/request-id_generated_frontside_social_gathering.jpg"
     ],
     "output_video_url": null,
     "excel_report_url": "http://YOUR-IP-ADDRESS/files/request-id_report.xlsx",
     "metadata": {}
   }
   ```

### How Files Are Currently Accessed
Files are served statically through the `/files` endpoint:
- URL pattern: `http://YOUR-IP-ADDRESS/files/{filename}`
- Files are stored in the `output` directory on the server

## Implemented Enhancement: GET Endpoint for File Access

### New GET Endpoint
A new endpoint has been implemented to retrieve file information by request_id:

```
GET /api/v1/files/{request_id}
```

### Implementation

1. **The endpoint has been added to `app/api/v1/endpoints/generate.py`:**

```python
@router.get("/files/{request_id}", response_model=FileAccessResponse)
async def get_files_by_request_id(request_id: str):
    """
    Retrieve all files associated with a specific request_id.
    
    Args:
        request_id: The unique identifier for the generation request
        
    Returns:
        FileAccessResponse with all file URLs for the request
    """
    try:
        # Validate request_id format (UUID)
        import uuid
        try:
            uuid.UUID(request_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid request_id format")
        
        # Check if the output directory exists
        output_dir = Path(settings.LOCAL_OUTPUT_DIR)
        if not output_dir.exists():
            raise HTTPException(status_code=500, detail="Output directory does not exist")
        
        # Find all files that contain the request_id in their filename
        files = []
        for file_path in output_dir.iterdir():
            if file_path.is_file() and request_id in file_path.name:
                # Construct the URL for accessing the file
                file_url = f"{settings.LOCAL_BASE_URL}/files/{file_path.name}"
                files.append({
                    "filename": file_path.name,
                    "url": file_url,
                    "type": get_file_type(file_path.name)
                })
        
        if not files:
            raise HTTPException(status_code=404, detail="No files found for this request_id")
        
        return {
            "request_id": request_id,
            "files": files,
            "count": len(files)
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving files: {str(e)}")
```

2. **The response model has been added to `app/schemas.py`:**

```python
class FileAccessResponse(BaseModel):
    request_id: str
    files: List[Dict[str, str]]
    count: int
    
    class Config:
        schema_extra = {
            "example": {
                "request_id": "123e4567-e89b-12d3-a456-426614174000",
                "files": [
                    {
                        "filename": "123e4567-e89b-12d3-a456-426614174000_generated_frontside.jpg",
                        "url": "http://YOUR-IP-ADDRESS/files/123e4567-e89b-12d3-a456-426614174000_generated_frontside.jpg",
                        "type": "image"
                    },
                    {
                        "filename": "123e4567-e89b-12d3-a456-426614174000_report.xlsx",
                        "url": "http://YOUR-IP-ADDRESS/files/123e4567-e89b-12d3-a456-426614174000_report.xlsx",
                        "type": "excel"
                    }
                ],
                "count": 2
            }
        }
```

## Usage Examples

### 1. POST Request (Existing Functionality)
```bash
curl -X POST "http://YOUR-IP-ADDRESS/api/v1/generate" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "frontside=@/path/to/image.jpg" \
  -F "text=woman dress, stylish, elegant, event wear" \
  -F "username=test_user" \
  -F "product=dress"
```

Response:
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

### 2. GET Request (New Functionality)
```bash
curl -X GET "http://YOUR-IP-ADDRESS/api/v1/files/123e4567-e89b-12d3-a456-426614174000"
```

Response:
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

## Implementation Steps

### Step 1: Add Response Model
The `FileAccessResponse` model has been added to `app/schemas.py`:

```python
class FileAccessResponse(BaseModel):
    request_id: str
    files: List[Dict[str, str]]
    count: int
```

### Step 2: Add GET Endpoint
The `get_files_by_request_id` function has been added to `app/api/v1/endpoints/generate.py`:

```python
@router.get("/files/{request_id}", response_model=FileAccessResponse)
async def get_files_by_request_id(request_id: str):
    # Implementation as shown above
```

### Step 3: Add Helper Function
The `get_file_type` helper function is already present in `app/api/v1/endpoints/generate.py`:

```python
def get_file_type(filename: str) -> str:
    """Determine file type based on extension."""
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    if ext in ['jpg', 'jpeg', 'png', 'gif']:
        return 'image'
    elif ext in ['mp4', 'avi', 'mov']:
        return 'video'
    elif ext in ['xlsx', 'xls']:
        return 'excel'
    elif ext in ['pdf']:
        return 'pdf'
    else:
        return 'other'
```

### Step 4: Import Required Modules
The necessary imports have been added at the top of `app/api/v1/endpoints/generate.py`:

```python
from app.schemas import GenerationResponse, ProcessingStatus, ErrorResponse, GenerationResult, FileAccessResponse
```

## Benefits of This System

1. **Easy File Access**: Retrieve all files for a request with a single GET request
2. **No Need to Store URLs**: You only need to remember the request_id
3. **Complete File List**: Get all generated files in one response
4. **File Type Information**: Know what type of file each one is
5. **Error Handling**: Proper error responses for invalid or missing request_ids

## Testing the Implementation

### Test Case 1: Valid Request ID
```bash
curl -X GET "http://YOUR-IP-ADDRESS/api/v1/files/VALID-REQUEST-ID"
```
Expected: 200 OK with file list

### Test Case 2: Invalid Request ID
```bash
curl -X GET "http://YOUR-IP-ADDRESS/api/v1/files/INVALID-REQUEST-ID"
```
Expected: 400 Bad Request or 404 Not Found

### Test Case 3: Non-existent Request ID
```bash
curl -X GET "http://YOUR-IP-ADDRESS/api/v1/files/00000000-0000-0000-0000-000000000000"
```
Expected: 404 Not Found

## Security Considerations

1. **Request ID Validation**: Validate that the request_id is a proper UUID format
2. **File Path Sanitization**: Ensure no directory traversal attacks are possible
3. **Access Control**: Consider adding authentication if needed for sensitive files
4. **Rate Limiting**: Implement rate limiting to prevent abuse

## Alternative Approach: Direct File Access

If you prefer to access files directly without an API endpoint:

1. Use the existing file URL pattern: `http://YOUR-IP-ADDRESS/files/{filename}`
2. You can construct these URLs using the request_id and known filename patterns
3. Files are already publicly accessible through the static file server

For example:
- Main image: `http://YOUR-IP-ADDRESS/files/{request_id}_generated_frontside.jpg`
- Report: `http://YOUR-IP-ADDRESS/files/{request_id}_report.xlsx`
- Variations: `http://YOUR-IP-ADDRESS/files/{request_id}_generated_{variation_name}.jpg`, etc.