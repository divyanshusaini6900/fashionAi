#!/bin/bash

# Script to fix the .env file for FashionModelingAI on GCP
# This switches from GCS to local storage to fix the "Server is not configured for GCS uploads" error

echo "Fixing .env file for FashionModelingAI..."

# Backup the current .env file
echo "Creating backup of current .env file..."
cp ~/fashionAi/.env ~/fashionAi/.env.backup

# Create the new .env file with local storage configuration
echo "Creating new .env file with local storage configuration..."
cat > ~/fashionAi/.env << 'EOF'
# API Keys - Replace with your actual API keys
OPENAI_API_KEY="your-openai-api-key-here"
REPLICATE_API_TOKEN="your-replicate-api-token-here"
GEMINI_API_KEY="your-gemini-api-key-here"

# AI Model Configuration
USE_GEMINI_FOR_IMAGES=true
USE_GEMINI_FOR_VIDEOS=true
USE_GEMINI_FOR_TEXT=true

# Storage Configuration - Using Local Storage (Recommended for GCP)
USE_LOCAL_STORAGE=true
LOCAL_BASE_URL="http://34.68.110.42"

# Application Settings
ENVIRONMENT=production
DEBUG=false
EOF

echo "Restarting fashion_ai service..."
sudo systemctl restart fashion_ai

echo "Fix applied! Check the service status with: sudo systemctl status fashion_ai"
echo "View logs with: sudo journalctl -u fashion_ai -f"
echo "Test your API at: http://34.68.110.42"