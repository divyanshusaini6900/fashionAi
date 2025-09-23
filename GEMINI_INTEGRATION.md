# Gemini API Integration Guide

This project now supports both **Gemini API** and **Replicate API** for image and video generation. You can choose which API to use through configuration.

## 🔧 Configuration

### Environment Variables (.env file):

```env
# API Keys
OPENAI_API_KEY="your-openai-key"
REPLICATE_API_TOKEN="your-replicate-token"
GEMINI_API_KEY="AIzaSyDwbvZ2wAQpekj5eQ93yEvTZd_IBCjvIvU"

# AI Model Configuration
USE_GEMINI_FOR_IMAGES=true    # Set to false to use Replicate
USE_GEMINI_FOR_VIDEOS=true    # Set to false to use Replicate

# Storage Configuration
USE_LOCAL_STORAGE=true
LOCAL_BASE_URL="http://localhost:8000"
```

## 🚀 How to Use

### Option 1: Use Gemini for Both Images and Videos (Default)
```env
USE_GEMINI_FOR_IMAGES=true
USE_GEMINI_FOR_VIDEOS=true
```

### Option 2: Use Replicate for Both
```env
USE_GEMINI_FOR_IMAGES=false
USE_GEMINI_FOR_VIDEOS=false
```

### Option 3: Mixed Usage
```env
USE_GEMINI_FOR_IMAGES=true   # Use Gemini for images
USE_GEMINI_FOR_VIDEOS=false  # Use Replicate for videos
```

## 🧪 Testing

### 1. Test the API Integration
```bash
python test_gemini_integration.py
```

### 2. Test the Full API
```bash
# Start the server
uvicorn app.main:app --reload

# In another terminal
python tests/run_api_test.py
```

## 📊 API Models Used

### Gemini API:
- **Images**: `imagen-4.0-generate-001`
- **Videos**: `veo-3.0-generate-001`

### Replicate API:
- **Images**: `flux-kontext-apps/multi-image-kontext-max`
- **Videos**: `kwaivgi/kling-v2.1`

## 🔄 Fallback Behavior

- If Gemini fails, the system automatically falls back to Replicate
- Both APIs are always available as backup
- Configuration can be changed without code modification

## 📝 Notes

1. **Video Generation**: Gemini video generation may take longer than Replicate
2. **Quality**: Both APIs produce high-quality results with different characteristics
3. **Cost**: Monitor your API usage for both services
4. **Local Testing**: You can test everything locally without cloud storage

## 🛠️ Installation

1. Install the new dependency:
```bash
pip install google-genai
```

2. Update your `.env` file with the Gemini API key

3. Start the server:
```bash
uvicorn app.main:app --reload
```

## ✅ Features Preserved

- ✅ All original features work exactly the same
- ✅ Local storage support
- ✅ Excel report generation
- ✅ Multiple image variations
- ✅ Product data analysis
- ✅ SKU generation
- ✅ All API endpoints unchanged

The integration is backward-compatible and non-breaking!