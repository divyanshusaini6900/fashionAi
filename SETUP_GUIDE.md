# Fashion AI API Setup Guide

This guide will help you set up and run the Fashion AI API to connect with your Flutter app.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Step 1: Set Up Python Environment

### Windows:

```powershell
# Navigate to fashionAi directory
cd fashionAi

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Mac/Linux:

```bash
# Navigate to fashionAi directory
cd fashionAi

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure Environment Variables

1. Open the `.env` file in the `fashionAi` directory
2. Add your API keys:
   - **OPENAI_API_KEY**: Get from https://platform.openai.com/api-keys
   - **REPLICATE_API_TOKEN**: Get from https://replicate.com/account/api-tokens
   - **GEMINI_API_KEY**: Get from https://aistudio.google.com/app/apikey

3. The `SERVICE_API_KEY` is already set to match your Flutter app

## Step 3: Run the API Server

```bash
# Make sure you're in the fashionAi directory with venv activated
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
🚀 Starting Fashion Modeling AI with Parallel Processing...
✅ Task queue system initialized
```

## Step 4: Test the API

Open your browser and go to:
- **API Root**: http://localhost:8000/
- **API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Step 5: Connect from Flutter App

Your Flutter app is already configured to connect to `http://127.0.0.1:8000/`, so once the API is running, your app should be able to connect.

## Available Endpoints

The Fashion AI API provides these main endpoints:

1. **POST /api/v1/generate** - Generate fashion images from uploaded files
2. **POST /api/v1/generate/image** - Generate fashion images from URLs (JSON)
3. **GET /api/v1/files/{request_id}** - Get generated files by request ID
4. **GET /api/v1/status/queue** - Check processing queue status

## Troubleshooting

### Port Already in Use
If port 8000 is already in use, you can change it:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

Then update your Flutter app's `lib/core/config/api_config.dart`:
```dart
static const String baseUrl = 'http://127.0.0.1:8080/';
```

### Missing Dependencies
If you get import errors, reinstall dependencies:
```bash
pip install -r requirements.txt --upgrade
```

### API Key Errors
Make sure all three API keys are set in the `.env` file:
- OPENAI_API_KEY
- REPLICATE_API_TOKEN
- GEMINI_API_KEY

## Running in Production

For production deployment, see:
- `GCP_DEPLOYMENT.md` - Google Cloud Platform deployment
- `NGINX_TROUBLESHOOTING.md` - Nginx configuration

## Notes

- The API uses parallel processing for better performance
- Generated files are stored in the `output` directory
- The API requires authentication via `x-api-key` header
- Your Flutter app is already configured with the correct API key

