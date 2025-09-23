# Deployment Guide: FashionModelingAI on Google Cloud Platform (GCP) - Step by Step for Beginners

This guide will teach you how to deploy the FashionModelingAI application on Google Cloud Platform step by step, just like following a recipe!

## What You'll Need (Prerequisites)

Before we start, make sure you have:
- A Google Cloud Platform account (like having a Google account but for computers)
- A credit card for billing (Google gives $300 free credit for new users)
- Your application's Google Cloud credentials
- Your OpenAI, Replicate, and Google Gemini API keys

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
3. Don't worry - Google gives you $300 free credit!

## Step 2: Set Up Your Virtual Machine (Computer in the Cloud)

### 2.1 Create a Compute Engine Instance
1. In the Google Cloud Console, type "Compute Engine" in the search bar and click it
2. Click "VM instances" in the left menu
3. Click "Create Instance"
4. Fill in these details:
   - Name: `fashion-ai-server`
   - Region: Choose one near you (like `us-central1`)
   - Zone: Choose any (like `us-central1-a`)
   - Machine type: `e2-medium`
   - Boot disk: `Ubuntu 22.04 LTS`
   - Firewall: Check both "Allow HTTP traffic" and "Allow HTTPS traffic"
5. Click "Create"

### 2.2 Connect to Your Virtual Machine
1. Wait for your VM to be created (it will show a green checkmark)
2. Click the "SSH" button next to your instance name
3. A new browser window will open - this is your terminal (command line)!

## Step 3: Install Software on Your Virtual Machine

### 3.1 Update Your System
In the terminal window that opened, type these commands one by one:
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
git clone https://github.com/your-username/FashionModelingAI.git
cd FashionModelingAI
```

### 4.2 Set Up Python Virtual Environment
Type these commands:
```bash
python3 -m venv fash_env
source fash_env/bin/activate
```

You should see `(fash_env)` at the beginning of your command line now!

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

This opens a text editor. Copy and paste this into it:
```env
# API Keys
OPENAI_API_KEY="your-openai-key"
REPLICATE_API_TOKEN="your-replicate-token"
GEMINI_API_KEY="your-gemini-key"

# Storage Configuration (Local Storage for now)
USE_LOCAL_STORAGE="true"
LOCAL_BASE_URL="http://localhost:8000"
```

To save and exit:
1. Press `Ctrl + X`
2. Press `Y`
3. Press `Enter`

## Step 6: Test Your Application

### 6.1 Run the Application
Type:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 6.2 Check if It's Working
1. Find your VM's external IP address:
   - Go back to the Google Cloud Console
   - Click "Compute Engine" → "VM instances"
   - Copy the external IP address (like 34.123.45.67)
2. Open a new browser tab
3. Go to `http://YOUR-IP-ADDRESS:8000` (replace with your actual IP)
4. You should see a message saying the API is running!

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
        alias /home/your-username/FashionModelingAI/generated_files/;
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

### 8.1 Create a Service File
Type:
```bash
sudo nano /etc/systemd/system/fashion_ai.service
```

Copy and paste this into the file (replace `your-username` with your actual username):
```ini
[Unit]
Description=Fashion AI FastAPI Application
After=network.target

[Service]
User=your-username
Group=your-username
WorkingDirectory=/home/your-username/FashionModelingAI
Environment="PATH=/home/your-username/FashionModelingAI/fash_env/bin"
EnvironmentFile=/home/your-username/FashionModelingAI/.env
ExecStart=/home/your-username/FashionModelingAI/fash_env/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app -b 0.0.0.0:8000

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

Press `Ctrl + C` to stop viewing the status.

## Step 9: Test Your Deployed Application

### 9.1 Visit Your Application
1. Open your browser
2. Go to `http://YOUR-IP-ADDRESS` (without the port number this time)
3. You should see the same message as before!

### 9.2 Test the API
1. Go to `http://YOUR-IP-ADDRESS/docs` to see the API documentation
2. Try the health check endpoint to make sure everything works

## Step 10: Set Up Cloud Storage (Optional)

If you want to store files in the cloud instead of on your VM:

### 10.1 Create a Cloud Storage Bucket
1. In Google Cloud Console, search for "Cloud Storage"
2. Click "Create Bucket"
3. Give it a name like `fashion-ai-storage`
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
3. Click the three dots menu in your terminal window
4. Click "Upload file"
5. Select your downloaded JSON key file
6. Maximize your terminal window

### 10.5 Update Your Environment File
Type:
```bash
nano .env
```

Change the contents to:
```env
# API Keys
OPENAI_API_KEY="your-openai-key"
REPLICATE_API_TOKEN="your-replicate-token"
GEMINI_API_KEY="your-gemini-key"

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

## Security Notes

1. Never share your `.env` file or API keys
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

## Congratulations!

You've successfully deployed your FashionModelingAI application to Google Cloud Platform! 🎉

Remember:
- Your application is now available at `http://YOUR-IP-ADDRESS`
- You can access the API documentation at `http://YOUR-IP-ADDRESS/docs`
- Your service will automatically restart if the VM reboots
- You can update your code by connecting via SSH and pulling from Git