# FashionModelingAI 🎭👗

An advanced AI-powered fashion modeling system that generates professional fashion product images and videos using state-of-the-art AI models. This system helps fashion businesses create high-quality product visualizations without the need for traditional photo shoots.

## 🌟 Features

- **AI Image Generation**: Transform basic product photos into professional model shots
- **Video Generation**: Create dynamic product videos from static images
- **Excel Report Generation**: Automatic generation of detailed product reports
- **Multi-View Support**: Process multiple angles (front, back, detail views)
- **Secure File Storage**: AWS S3 integration for reliable file management
- **RESTful API**: Easy integration with existing e-commerce platforms
- **Customizable Outputs**: Control style, background, and model characteristics

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **AI Models**:
  - OpenAI for image generation
  - Replicate for video processing
- **Storage**: AWS S3
- **Documentation**: OpenAPI/Swagger
- **Deployment**: AWS EC2, Nginx, Gunicorn

## 📋 Prerequisites

Before setting up the project, ensure you have:

- Python 3.8 or higher
- pip (Python package manager)
- AWS account with S3 access
- OpenAI API key
- Replicate API token
- Git

## 🚀 Quick Start

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your-username/FashionModelingAI.git
   cd FashionModelingAI
   ```

2. **Set Up Virtual Environment**

   ```bash
   python -m venv fash_env
   source fash_env/bin/activate  # On Windows: fash_env\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   Create a `.env` file in the project root:

   ```env
   # API Keys
   OPENAI_API_KEY="your-openai-key"
   REPLICATE_API_TOKEN="your-replicate-token"

   # AWS Configuration
   S3_BUCKET_NAME="your-bucket-name"
   AWS_ACCESS_KEY_ID="your-access-key"
   AWS_SECRET_ACCESS_KEY="your-secret-key"
   AWS_REGION="us-east-1"
   ```

5. **Run the Application**

   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

## 📁 Project Structure

```
FashionModelingAI/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           └── generate.py    # Main API endpoints
│   ├── core/
│   │   ├── config.py             # Configuration management
│   │   └── security.py           # Security utilities
│   ├── services/
│   │   ├── excel_generator.py    # Excel report generation
│   │   ├── image_generator.py    # AI image generation
│   │   └── video_generator.py    # Video processing
│   └── utils/
│       └── file_helpers.py       # File handling utilities
├── tests/
│   └── test_generate.py          # API tests
└── requirements.txt              # Project dependencies
```

## 🔄 API Endpoints

### Generate Fashion Content

```http
POST /api/v1/generate
```

**Request Body (multipart/form-data):**

- `frontside`: Required - Front view image
- `backside`: Optional - Back view image
- `detailview`: Optional - Detail view image
- `text`: Description of desired output
- `username`: User identifier
- `product`: Product type
- `generate_video`: Boolean flag for video generation

**Response:**

```json
{
  "output_image_url": "https://...",
  "output_video_url": "https://...",
  "excel_report_url": "https://..."
}
```

## 🧪 Running Tests

```bash
# Run sample test
python tests/run_api_test.py
```

## 📝 Example Usage

Here's a Python script demonstrating how to use the API:

```python
import requests

# API endpoint
url = "http://localhost:8000/api/v1/generate"

# Prepare files and data
files = {
    "frontside": ("front.jpg", open("front.jpg", "rb"), "image/jpeg"),
    "detailview": ("detail.jpg", open("detail.jpg", "rb"), "image/jpeg")
}

data = {
    "text": "woman dress, stylish, elegant, event wear",
    "username": "test_user",
    "product": "dress",
    "generate_video": "true"
}

# Send request
response = requests.post(url, files=files, data=data)

# Process response
if response.status_code == 200:
    result = response.json()
    print(f"Image URL: {result['output_image_url']}")
    print(f"Video URL: {result['output_video_url']}")
    print(f"Report URL: {result['excel_report_url']}")
```

## 🔒 Security Considerations

1. **API Keys**: Never commit `.env` file or expose API keys
2. **File Validation**: The system validates file types and sizes
3. **S3 Security**: Bucket is configured for secure uploads with public read access
4. **Rate Limiting**: API endpoints include rate limiting
5. **Input Sanitization**: All inputs are validated and sanitized

## 🚧 Error Handling

The API uses standard HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid input)
- `401`: Unauthorized
- `403`: Forbidden
- `500`: Server Error

Detailed error messages are provided in the response body.

## 📈 Performance Considerations

- Image processing is handled asynchronously
- File uploads are streamed to minimize memory usage
- S3 integration includes retry logic
- Caching implemented for frequent requests
- Configurable worker processes for scalability

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 🔄 Updates and Maintenance

- Regular dependency updates
- Security patches as needed
- Performance optimization
- Feature additions based on feedback

## 🌟 Acknowledgments

- OpenAI for image generation capabilities
- Replicate for video processing
- FastAPI framework
- AWS for infrastructure support
