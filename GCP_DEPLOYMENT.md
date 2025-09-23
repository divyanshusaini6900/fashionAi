# Deployment Guide: FashionModelingAI on Google Cloud Platform (GCP) - Updated Version

This guide will walk you through deploying the FashionModelingAI application on Google Cloud Platform step by step, making it easy for anyone to follow!

## What You'll Need (Prerequisites)

Before we start, make sure you have:
- A Google Cloud Platform account (like a Gmail account but for cloud computing)
- A credit card for billing (Google gives $300 free credit for new users - you won't be charged unless you exceed this)
- Your application's API keys:
  - OpenAI API key
  - Replicate API token
  - Google Gemini API key

## Step 1: Set Up Your Google Cloud Account

### 1.1 Create a Google Cloud Project
1. Open your web browser (like Chrome or Firefox)
2. Go to [https://console.cloud.google.com/](https://console.cloud.google.com/)
3. Click on the project dropdown at the top (it might say "Select a project")
4. Click "New Project"
5. Give your project a name like "fashion-ai-project"
6. Click "Create"

### 1.2 Enable Billing
1. In the left menu, click "Billing"
2. Follow the prompts to add your credit card
3. Don't worry - Google gives you $300 free credit for new accounts!

## Step 2: Set Up Your Virtual Machine (Computer in the Cloud)

### 2.1 Create a Compute Engine Instance
1. In the Google Cloud Console, type "Compute Engine" in the search bar at the top and click it
2. Click "VM instances" in the left menu
3. Click "Create Instance"
4. Fill in these details:
   - Name: `fashion-ai-server`
   - Region: Choose one near you (like `us-central1` for US, `europe-west1` for Europe)
   - Zone: Choose any (like `us-central1-a`)
   - Machine type: `e2-medium` (this is enough for our application)
   - Boot disk: `Ubuntu 22.04 LTS` (this is the operating system)
   - Firewall: Check both "Allow HTTP traffic" and "Allow HTTPS traffic"
5. Click "Create" at the bottom

### 2.2 Connect to Your Virtual Machine
1. Wait for your VM to be created (it will show a green checkmark when ready)
2. Click the blue "SSH" button next to your instance name
3. A new browser window will open - this is your terminal (command line) where you'll type commands!

## Step 3: Install Software on Your Virtual Machine

### 3.1 Update Your System
In the terminal window that opened, type these commands one by one (press Enter after each):
```bash
sudo apt update
sudo apt upgrade -y
```

### 3.2 Install Required Software
Type these commands one by one:
```bash
sudo apt install python3-pip python3-venv nginx -y
sudo apt install build-essential libssl-dev libffi-dev python3-dev -y
```

## Step 4: Download Your Application Code

### 4.1 Clone the Repository
In the same terminal, type:
```bash
git clone https://github.com/divyanshusaini6900/fashionAi.git
cd fashionAi
```

### 4.2 Set Up Python Virtual Environment
Type these commands:
```bash
python3 -m venv fash_env
source fash_env/bin/activate
```

You should see `(fash_env)` at the beginning of your command line now! This means you're in the right environment.

### 4.3 Install Python Dependencies
Type:
```bash
pip install -r requirements.txt
pip install gunicorn
```

## Step 5: Configure Your Application

### 5.1 Create Environment File
Type:
```bash
nano .env
```

This opens a text editor. Copy and paste this into it (replace the placeholder keys with your actual API keys):
```env
# API Keys - REPLACE THESE WITH YOUR ACTUAL KEYS
OPENAI_API_KEY="your-real-openai-api-key-here"
REPLICATE_API_TOKEN="your-real-replicate-api-token-here"
GEMINI_API_KEY="your-real-gemini-api-key-here"

# Storage Configuration (Local Storage for now)
USE_LOCAL_STORAGE="true"
LOCAL_BASE_URL="http://localhost:8000"
```

To save and exit:
1. Press `Ctrl + X` (this means "exit")
2. Press `Y` (this means "yes, save the file")
3. Press `Enter` (this confirms the filename)

## Step 6: Test Your Application

### 6.1 Run the Application
Type:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 6.2 Check if It's Working
1. Find your VM's external IP address:
   - Go back to the Google Cloud Console (you can open a new tab)
   - Click "Compute Engine" → "VM instances"
   - Find your instance and copy the external IP address (looks like 34.123.45.67)
2. Open a new browser tab
3. Go to `http://YOUR-IP-ADDRESS:8000` (replace YOUR-IP-ADDRESS with the actual IP you copied)
4. You should see a message saying "Fashion Modeling AI API is running" with status "healthy"!

### 6.3 Stop the Application
Go back to your terminal and press `Ctrl + C` to stop the application.

## Step 7: Set Up Nginx (Web Server)

### 7.1 Create Nginx Configuration
Type:
```bash
sudo nano /etc/nginx/sites-available/fashion_ai
```

Copy and paste this into the file:
```nginx
server {
    listen 80;
    server_name your-domain-or-ip;

    location = /favicon.ico { access_log off; log_not_found off; }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Serve generated files directly
    location /files/ {
        alias /home/your-username/fashionAi/generated_files/;
    }

    # Increase max upload size
    client_max_body_size 10M;
}
```

To save and exit:
1. Press `Ctrl + X`
2. Press `Y`
3. Press `Enter`

### 7.2 Enable the Configuration
Type these commands:
```bash
sudo ln -s /etc/nginx/sites-available/fashion_ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 8: Set Up Your Application as a Service

This step makes your application run automatically even if the server restarts.

### 8.1 Create a Service File
Type:
```bash
sudo nano /etc/systemd/system/fashion_ai.service
```

Copy and paste this into the file (replace `your-username` with your actual username - you can find it by typing `whoami` in the terminal):
```ini
[Unit]
Description=Fashion AI FastAPI Application
After=network.target

[Service]
User=your-username
Group=your-username
WorkingDirectory=/home/your-username/fashionAi
Environment="PATH=/home/your-username/fashionAi/fash_env/bin"
EnvironmentFile=/home/your-username/fashionAi/.env
ExecStart=/home/your-username/fashionAi/fash_env/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app -b 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

To save and exit:
1. Press `Ctrl + X`
2. Press `Y`
3. Press `Enter`

### 8.2 Start and Enable the Service
Type these commands:
```bash
sudo systemctl start fashion_ai
sudo systemctl enable fashion_ai
sudo systemctl status fashion_ai
```

You should see the service is active (running). Press `Ctrl + C` to stop viewing the status.

## Step 9: Test Your Deployed Application

### 9.1 Visit Your Application
1. Open your browser
2. Go to `http://YOUR-IP-ADDRESS` (without the port number this time - just the IP address)
3. You should see the same message as before!

### 9.2 Test the API
1. Go to `http://YOUR-IP-ADDRESS/docs` to see the API documentation
2. Try the health check endpoint by clicking "Try it out" and then "Execute"

## Step 10: Set Up Cloud Storage (Optional but Recommended)

If you want to store files in the cloud instead of on your VM (recommended for production):

### 10.1 Create a Cloud Storage Bucket
1. In Google Cloud Console, search for "Cloud Storage"
2. Click "Create Bucket"
3. Give it a name like `fashion-ai-storage` (must be globally unique)
4. Choose a location (like `us-central1`)
5. Keep other settings as default
6. Click "Create"

### 10.2 Create a Service Account
1. Search for "IAM & Admin" → "Service Accounts"
2. Click "Create Service Account"
3. Name it `fashion-ai-service-account`
4. Click "Create and Continue"
5. Click "Select a role" and choose "Storage Admin"
6. Click "Continue" then "Done"

### 10.3 Create a Key for the Service Account
1. Click on your new service account
2. Go to the "Keys" tab
3. Click "Add Key" → "Create New Key"
4. Select "JSON" format
5. Click "Create"
6. Save this file to your computer (we'll upload it to your VM)

### 10.4 Upload the Key to Your VM
1. In your VM terminal, type:
```bash
mkdir -p ~/keys
```
2. Minimize your terminal window
3. Click the three dots menu (⋮) in your terminal window
4. Click "Upload file"
5. Select your downloaded JSON key file
6. Maximize your terminal window

### 10.5 Update Your Environment File
Type:
```bash
nano .env
```

Change the contents to (replace `your-bucket-name` and `your-key-file.json` with actual values):
```env
# API Keys - REPLACE THESE WITH YOUR ACTUAL KEYS
OPENAI_API_KEY="your-real-openai-api-key-here"
REPLICATE_API_TOKEN="your-real-replicate-api-token-here"
GEMINI_API_KEY="your-real-gemini-api-key-here"

# Storage Configuration (Cloud Storage)
USE_LOCAL_STORAGE="false"
GCS_BUCKET_NAME="your-bucket-name"
GOOGLE_APPLICATION_CREDENTIALS="/home/your-username/keys/your-key-file.json"
```

Save and exit (Ctrl+X, Y, Enter)

### 10.6 Restart Your Application
Type:
```bash
sudo systemctl restart fashion_ai
```

## Step 11: Test Your API with Sample Data

### 11.1 Using the API Documentation Interface
1. Go to `http://YOUR-IP-ADDRESS/docs` (replace YOUR-IP-ADDRESS with your actual IP like 34.68.110.42)
2. Find the "POST /api/v1/generate" endpoint
3. Click "Try it out"
4. For testing purposes, you can use sample images:
   - Download a sample clothing image from the internet or use your own
   - Upload it as the "frontside" parameter
   - Fill in the required text fields:
     - text: "woman dress, stylish, elegant, event wear"
     - username: "test_user"
     - product: "dress"
5. Click "Execute"
6. Wait for the response (this may take 30-60 seconds)

### 11.2 Using Postman (Recommended for Testing)
1. Download and install [Postman](https://www.postman.com/downloads/)
2. Create a new request:
   - Method: POST
   - URL: `http://YOUR-IP-ADDRESS/api/v1/generate` (replace YOUR-IP-ADDRESS)
3. Go to the "Body" tab
4. Select "form-data"
5. Add the following key-value pairs:
   - Key: `frontside`, Value: [Select a clothing image file by clicking "Select Files"]
   - Key: `text`, Value: "woman dress, stylish, elegant, event wear"
   - Key: `username`, Value: "test_user"
   - Key: `product`, Value: "dress"
6. Click "Send"
7. Wait for the response (this may take 30-60 seconds)

### 11.3 Using cURL from Command Line
You can also test using cURL from any terminal:
```bash
curl -X POST "http://YOUR-IP-ADDRESS/api/v1/generate" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "frontside=@/path/to/your/image.jpg" \
  -F "text=woman dress, stylish, elegant, event wear" \
  -F "username=test_user" \
  -F "product=dress"
```

### 11.4 Expected Response
A successful response will look like this:
```json
{
  "request_id": "unique-request-id",
  "output_image_url": "http://YOUR-IP-ADDRESS/files/generated/request-id/image.jpg",
  "image_variations": [
    "http://YOUR-IP-ADDRESS/files/generated/request-id/variation1.jpg"
  ],
  "output_video_url": null,
  "excel_report_url": "http://YOUR-IP-ADDRESS/files/generated/request-id/report.xlsx",
  "metadata": {
    // Additional information about the generation process
  }
}
```

### 11.5 Testing with Sample Images
If you don't have sample images, you can:
1. Use royalty-free images from sites like [Unsplash](https://unsplash.com/) or [Pexels](https://pexels.com/)
2. Search for "fashion model" or "clothing item" images
3. Make sure they are JPG or PNG format
4. Keep file sizes under 5MB for best results

## Troubleshooting Common Issues

### If Your Website Doesn't Load
1. Check if your service is running:
```bash
sudo systemctl status fashion_ai
```
2. Check Nginx:
```bash
sudo systemctl status nginx
```
3. Check logs:
```bash
sudo journalctl -u fashion_ai -f
```
Press `Ctrl + C` to stop viewing logs.

### If You Get Permission Errors
Make sure your files have the right permissions:
```bash
chmod 644 .env
```

### If Nginx Configuration Fails
Check for typos in your configuration file:
```bash
sudo nginx -t
```

### If API Requests Fail
1. Check if the service is running: `sudo systemctl status fashion_ai`
2. Check application logs: `sudo journalctl -u fashion_ai -f`
3. Verify your API keys in the `.env` file
4. Make sure you're not exceeding file size limits

### If File Uploads Don't Work
1. Check Nginx client max body size:
   ```bash
   sudo nano /etc/nginx/sites-available/fashion_ai
   ```
   Make sure `client_max_body_size 10M;` is set
2. Restart Nginx:
   ```bash
   sudo systemctl restart nginx
   ```

## Security Notes

1. Never share your `.env` file or API keys with anyone
2. Keep your service account key file secure
3. Regularly update your system with:
```bash
sudo apt update && sudo apt upgrade -y
```

## Monitoring Your Application

Check your application logs anytime with:
```bash
sudo journalctl -u fashion_ai -f
```
Press `Ctrl + C` to stop.

Check Nginx logs with:
```bash
sudo tail -f /var/log/nginx/error.log
```
Press `Ctrl + C` to stop.

## Updating Your Application

To update your code when you make changes:
```bash
git pull
sudo systemctl restart fashion_ai
```

## Congratulations!

You've successfully deployed your FashionModelingAI application to Google Cloud Platform! 🎉

Remember:
- Your application is now available at `http://YOUR-IP-ADDRESS`
- You can access the API documentation at `http://YOUR-IP-ADDRESS/docs`
- Your service will automatically restart if the VM reboots
- You can update your code by connecting via SSH and pulling from Git

### Quick Reference Commands:
- Check service status: `sudo systemctl status fashion_ai`
- Restart service: `sudo systemctl restart fashion_ai`
- View logs: `sudo journalctl -u fashion_ai -f`
- Update code: `git pull` then `sudo systemctl restart fashion_ai`
- Check Nginx: `sudo systemctl status nginx`

If you ever need to make changes to your configuration:
1. Edit the `.env` file: `nano .env`
2. Restart the service: `sudo systemctl restart fashion_ai`