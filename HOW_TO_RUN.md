# How to Run FashionModelingAI Locally and Test with Postman

This guide explains how to set up, run, and test the FashionModelingAI project on your local machine using Postman.

## Prerequisites

1. Python 3.8 or higher
2. [Postman](https://www.postman.com/downloads/) installed
3. API keys for:
   - OpenAI
   - Replicate
   - Google Gemini

## Setup Instructions

### 1. Clone the Repository (if not already done)
```bash
git clone https://github.com/your-username/FashionModelingAI.git
cd FashionModelingAI
```

### 2. Set Up Virtual Environment
```bash
# Windows
python -m venv fash_env
fash_env\Scripts\activate

# macOS/Linux
python3 -m venv fash_env
source fash_env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root by copying the example:
```bash
cp .env.example .env
```

Then edit the `.env` file and add your API keys:
```env
# API Keys - Required for AI services
OPENAI_API_KEY=your_openai_api_key_here
REPLICATE_API_TOKEN=your_replicate_api_token_here
GEMINI_API_KEY=your_gemini_api_key_here

# AWS Configuration (optional for local development)
S3_BUCKET_NAME=your_s3_bucket_name
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=ap-south-1
```

## Running the Application

### Start the Server
```bash
python -m uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

### Verify the Server is Running
Visit `http://127.0.0.1:8000` in your browser or use curl:
```bash
curl http://127.0.0.1:8000
```

You should see a response like:
```json
{
  "message": "Fashion Modeling AI API is running",
  "status": "healthy",
  "version": "1.0.0"
}
```

## Testing with Postman

### 1. Import Postman Collection and Environment
1. Open Postman
2. Click "Import" in the top left
3. Select the following files from the `postman` directory:
   - `FashionModelingAI_Collection.json`
   - `FashionModelingAI_Environment.json`
4. Click "Import"

### 2. Select the Environment
1. In Postman, select "FashionModelingAI Local" from the environment dropdown (top right)

### 3. Test the API Endpoints

#### Health Check
1. Select the "Health Check" request in the collection
2. Click "Send"
3. You should receive a success response

#### Generate Fashion Content
1. Select the "Generate Fashion Content" request
2. In the "Body" tab, make sure form-data is selected
3. For the `frontside` field:
   - Click "Select Files"
   - Choose an image file (you can use one from `tests/test_data/`)
4. Fill in the required text fields:
   - `text`: "woman dress, stylish, elegant, event wear"
   - `username`: "test_user"
   - `product`: "dress"
5. Click "Send"

### Expected Response
A successful response will look like:
```json
{
  "request_id": "unique-request-id",
  "output_image_url": "http://127.0.0.1:8000/files/generated/request-id/image.jpg",
  "image_variations": [
    "http://127.0.0.1:8000/files/generated/request-id/variation1.jpg"
  ],
  "output_video_url": null,
  "excel_report_url": "http://127.0.0.1:8000/files/generated/request-id/report.xlsx",
  "metadata": {
    // Additional information about the generation process
  }
}
```

## Direct API Testing (Alternative to Postman)

You can also test the API using the provided Python script:
```bash
python test_api_with_postman_data.py
```

## Project Structure

```
FashionModelingAI/
├── app/                    # Main application code
│   ├── api/v1/endpoints/  # API endpoints
│   ├── core/              # Configuration and settings
│   ├── services/          # Business logic
│   └── utils/             # Utility functions
├── tests/                 # Test files and test data
├── postman/               # Postman collection and environment
├── .env.example           # Environment variables template
├── requirements.txt       # Python dependencies
└── HOW_TO_RUN.md          # This file
```

## Troubleshooting

### Common Issues

1. **Module not found errors**: Make sure you've activated the virtual environment and installed dependencies
2. **API key errors**: Verify all required API keys are set in your `.env` file
3. **Port already in use**: Change the port using `--port` flag: `uvicorn app.main:app --reload --port 8001`
4. **File upload errors**: Ensure image files are in JPEG or PNG format

### Checking Logs
When running the server, you'll see logs in the terminal that can help diagnose issues:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Started server process
INFO:     Waiting for application startup
INFO:     Application startup complete
```

## API Endpoints

### GET /
Health check endpoint

### POST /api/v1/generate
Main generation endpoint with the following form fields:
- `frontside` (required): Front view image
- `text` (required): Product description
- `username` (required): User identifier
- `product` (required): Product type
- `generate_video` (optional): Boolean for video generation
- `numberOfOutputs` (optional): Number of image variations (1-4)
- `backside` (optional): Back view image
- `sideview` (optional): Side view image
- `detailview` (optional): Detail view image

## Stopping the Server
Press `Ctrl+C` in the terminal where the server is running.