# Visual Step-by-Step GCP Deployment Guide

## Step 1: Create Google Cloud Project

### 1.1 Go to Google Cloud Console
**What you'll see:** Google Cloud Console homepage
**What to do:**
1. Click on the project dropdown at the top
2. Click "New Project"
3. Enter project name: `fashion-ai-project`
4. Click "Create"

*SCREENSHOT PLACEHOLDER: Project creation screen*

### 1.2 Enable Billing
**What you'll see:** Billing setup page
**What to do:**
1. Click "Billing" in the left navigation menu
2. Click "Link a billing account"
3. Add your credit card information
4. Confirm

*SCREENSHOT PLACEHOLDER: Billing setup screen*

## Step 2: Create Virtual Machine

### 2.1 Navigate to Compute Engine
**What you'll see:** Google Cloud navigation menu
**What to do:**
1. Type "Compute Engine" in the search bar
2. Click on "Compute Engine" in search results
3. Click "VM instances" in the left menu
4. Click "Create Instance"

*SCREENSHOT PLACEHOLDER: Compute Engine navigation*

### 2.2 Configure Your VM
**What you'll see:** VM creation form
**What to do:**
1. Name: `fashion-ai-server`
2. Region: `us-central1` (or nearest to you)
3. Zone: `us-central1-a`
4. Machine type: `e2-medium`
5. Boot disk: `Ubuntu 22.04 LTS`
6. Check "Allow HTTP traffic"
7. Check "Allow HTTPS traffic"
8. Click "Create"

*SCREENSHOT PLACEHOLDER: VM configuration form*

### 2.3 Connect to Your VM
**What you'll see:** VM instances list with your new VM
**What to do:**
1. Wait for your VM to show a green checkmark (RUNNING)
2. Click the "SSH" button in the "Connect" column
3. A new browser window opens - this is your terminal!

*SCREENSHOT PLACEHOLDER: VM instances list with SSH button*

## Step 3: Install Software in Terminal

### 3.1 Update System
**What you'll see:** Terminal command prompt
**What to type:**
```bash
sudo apt update
sudo apt upgrade -y
```

*SCREENSHOT PLACEHOLDER: Terminal with update commands*

### 3.2 Install Required Software
**What to type:**
```bash
sudo apt install python3-pip python3-venv nginx -y
sudo apt install build-essential libssl-dev libffi-dev python3-dev -y
```

*SCREENSHOT PLACEHOLDER: Terminal with install commands*

## Step 4: Download and Set Up Application

### 4.1 Clone Repository
**What to type:**
```bash
git clone https://github.com/your-username/FashionModelingAI.git
cd FashionModelingAI
```

*SCREENSHOT PLACEHOLDER: Terminal with git clone command*

### 4.2 Create Python Virtual Environment
**What to type:**
```bash
python3 -m venv fash_env
source fash_env/bin/activate
```

**What you should see:** `(fash_env)` at the beginning of your command prompt

*SCREENSHOT PLACEHOLDER: Terminal with virtual environment activated*

### 4.3 Install Python Dependencies
**What to type:**
```bash
pip install -r requirements.txt
pip install gunicorn
```

*SCREENSHOT PLACEHOLDER: Terminal with pip install commands*

## Step 5: Configure Environment Variables

### 5.1 Create .env File
**What to type:**
```bash
nano .env
```

*SCREENSHOT PLACEHOLDER: Terminal with nano command*

### 5.2 Edit .env File
**What to type in the editor:**
```env
OPENAI_API_KEY="your-real-openai-key-here"
REPLICATE_API_TOKEN="your-real-replicate-key-here"
GEMINI_API_KEY="your-real-gemini-key-here"
USE_LOCAL_STORAGE="true"
LOCAL_BASE_URL="http://localhost:8000"
```

*SCREENSHOT PLACEHOLDER: Nano editor with .env content*

### 5.3 Save .env File
**What to do:**
1. Press `Ctrl + X`
2. Press `Y`
3. Press `Enter`

*SCREENSHOT PLACEHOLDER: Nano save confirmation*

## Step 6: Test Application

### 6.1 Run Application
**What to type:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

*SCREENSHOT PLACEHOLDER: Terminal running uvicorn*

### 6.2 Find Your VM's External IP
**What to do:**
1. Go back to Google Cloud Console
2. Navigate to "Compute Engine" → "VM instances"
3. Find the "External IP" column for your VM

*SCREENSHOT PLACEHOLDER: VM instances list showing external IP*

### 6.3 Test in Browser
**What to do:**
1. Open a new browser tab
2. Go to `http://YOUR-EXTERNAL-IP:8000`
3. You should see the API health check message

*SCREENSHOT PLACEHOLDER: Browser showing API health check*

### 6.4 Stop Application
**What to do:**
1. Go back to your terminal
2. Press `Ctrl + C`

*SCREENSHOT PLACEHOLDER: Terminal after Ctrl+C*

## Step 7: Set Up Nginx Web Server

### 7.1 Create Nginx Configuration
**What to type:**
```bash
sudo nano /etc/nginx/sites-available/fashion_ai
```

*SCREENSHOT PLACEHOLDER: Terminal with nano command for nginx config*

### 7.2 Edit Nginx Configuration
**What to type in the editor:**
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

    location /files/ {
        alias /home/your-username/FashionModelingAI/generated_files/;
    }

    client_max_body_size 10M;
}
```

*SCREENSHOT PLACEHOLDER: Nano editor with nginx config*

### 7.3 Save and Enable Configuration
**What to type:**
```bash
sudo ln -s /etc/nginx/sites-available/fashion_ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

*SCREENSHOT PLACEHOLDER: Terminal with nginx commands*

## Step 8: Create System Service

### 8.1 Create Service File
**What to type:**
```bash
sudo nano /etc/systemd/system/fashion_ai.service
```

*SCREENSHOT PLACEHOLDER: Terminal with nano command for service file*

### 8.2 Edit Service File
**What to type in the editor (replace "your-username"):**
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

*SCREENSHOT PLACEHOLDER: Nano editor with service config*

### 8.3 Save and Start Service
**What to type:**
```bash
sudo systemctl start fashion_ai
sudo systemctl enable fashion_ai
```

*SCREENSHOT PLACEHOLDER: Terminal with systemctl commands*

## Step 9: Final Test

### 9.1 Test Without Port Number
**What to do:**
1. Open browser
2. Go to `http://YOUR-EXTERNAL-IP` (without :8000)
3. You should see the same success message

*SCREENSHOT PLACEHOLDER: Browser showing final test*

### 9.2 Test API Documentation
**What to do:**
1. Go to `http://YOUR-EXTERNAL-IP/docs`
2. You should see the API documentation

*SCREENSHOT PLACEHOLDER: Browser showing API documentation*

## Useful Commands Reference

### Check Service Status
```bash
sudo systemctl status fashion_ai
```

### Restart Service
```bash
sudo systemctl restart fashion_ai
```

### View Application Logs
```bash
sudo journalctl -u fashion_ai -f
```
(Press `Ctrl + C` to stop)

### View Nginx Logs
```bash
sudo tail -f /var/log/nginx/error.log
```
(Press `Ctrl + C` to stop)

### Update Application Code
```bash
git pull
sudo systemctl restart fashion_ai
```

## Troubleshooting Visual Guide

### Service Not Running
*SCREENSHOT PLACEHOLDER: systemctl status showing failed service*

### Nginx Configuration Error
*SCREENSHOT PLACEHOLDER: nginx -t showing configuration error*

### Permission Denied Error
*SCREENSHOT PLACEHOLDER: Permission error in logs*

### Application Not Responding
*SCREENSHOT PLACEHOLDER: Browser showing connection refused*

## Congratulations! 🎉

You've successfully deployed your FashionModelingAI application to Google Cloud Platform!

*SCREENSHOT PLACEHOLDER: Browser showing successful deployment*