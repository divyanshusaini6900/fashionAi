@echo off
echo Fixing .env file for FashionModelingAI...

echo Creating backup of current .env file...
copy "C:\Users\LENOVO\Desktop\fashion\FashionModelingAI-master\.env" "C:\Users\LENOVO\Desktop\fashion\FashionModelingAI-master\.env.backup"

echo Creating new .env file with local storage configuration...
(
echo # API Keys - Replace with your actual API keys
echo OPENAI_API_KEY="your-openai-api-key-here"
echo REPLICATE_API_TOKEN="your-replicate-api-token-here"
echo GEMINI_API_KEY="your-gemini-api-key-here"
echo.
echo # AI Model Configuration
echo USE_GEMINI_FOR_IMAGES=true
echo USE_GEMINI_FOR_VIDEOS=true
echo USE_GEMINI_FOR_TEXT=true
echo.
echo # Storage Configuration - Using Local Storage (Recommended for GCP)
echo USE_LOCAL_STORAGE=true
echo LOCAL_BASE_URL="http://34.68.110.42"
echo.
echo # Application Settings
echo ENVIRONMENT=production
echo DEBUG=false
) > "C:\Users\LENOVO\Desktop\fashion\FashionModelingAI-master\.env"

echo.
echo Fix applied! Now you need to:
echo 1. Upload the new .env file to your server
echo 2. Restart your fashion_ai service with: sudo systemctl restart fashion_ai
echo 3. Check the service status with: sudo systemctl status fashion_ai
pause