# Super Simple GCP Deployment Guide - Like a Checklist!

## Before You Start - What You Need 🛠️

- [ ] Google Account (like Gmail)
- [ ] Credit Card (Google gives $300 free!)
- [ ] API Keys:
  - [ ] OpenAI Key
  - [ ] Replicate Key
  - [ ] Google Gemini Key

## Step 1: Google Cloud Setup ☁️

### Open Browser → Go to console.cloud.google.com

- [ ] Click "Select a project" → "New Project"
- [ ] Name it "fashion-ai-project"
- [ ] Click "Create"

### Enable Billing

- [ ] Click "Billing" in left menu
- [ ] Add your credit card

## Step 2: Create Your Computer in the Cloud 💻

### In Google Cloud Console:

- [ ] Search "Compute Engine" → Click it
- [ ] Click "VM instances"
- [ ] Click "Create Instance"
- [ ] Fill this exactly:
  - Name: `fashion-ai-server`
  - Region: `us-central1`
  - Machine type: `e2-medium`
  - Boot disk: `Ubuntu 22.04 LTS`
  - Check "Allow HTTP traffic"
  - Check "Allow HTTPS traffic"
- [ ] Click "Create"

### Connect to Your Computer:

- [ ] Wait for green checkmark
- [ ] Click "SSH" button
- [ ] New window opens - THIS IS YOUR TERMINAL!

## Step 3: Install Software on Your Cloud Computer ⬇️

### In the Terminal Window (type these exactly):

```
sudo apt update
sudo apt upgrade -y
sudo apt install python3-pip python3-venv nginx -y
sudo apt install build-essential libssl-dev libffi-dev python3-dev -y
```

## Step 4: Get Your Application Code 📥

### In the Same Terminal:

```
git clone https://github.com/your-username/FashionModelingAI.git
cd FashionModelingAI
python3 -m venv fash_env
source fash_env/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

## Step 5: Configure Your App ⚙️

### Create Configuration File:

```
nano .env
```

### COPY THIS EXACTLY (replace with your real keys):

```
OPENAI_API_KEY="your-real-openai-key-here"
REPLICATE_API_TOKEN="your-real-replicate-key-here"
GEMINI_API_KEY="your-real-gemini-key-here"
USE_LOCAL_STORAGE="true"
LOCAL_BASE_URL="http://localhost:8000"
```

### Save It:

1. Press `Ctrl + X`
2. Press `Y`
3. Press `Enter`

## Step 6: Test It Works ✅

### Run Your App:

```
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Check It:

1. Go back to Google Cloud Console
2. Find your VM's EXTERNAL IP (like 34.123.45.67)
3. Open new browser tab
4. Go to `http://YOUR-IP:8000`
5. You should see "Fashion Modeling AI API is running"!

### Stop the App:

- Go back to terminal
- Press `Ctrl + C`

## Step 7: Set Up Web Server 🌐

### Create Nginx File:

```
sudo nano /etc/nginx/sites-available/fashion_ai
```

### COPY THIS EXACTLY:

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

### Save It:

1. Press `Ctrl + X`
2. Press `Y`
3. Press `Enter`

### Enable It:

```
sudo ln -s /etc/nginx/sites-available/fashion_ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 8: Make It Run Forever 🔁

### Create Service File:

```
sudo nano /etc/systemd/system/fashion_ai.service
```

### COPY THIS (replace "your-username" with actual username):

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

### Save It:

1. Press `Ctrl + X`
2. Press `Y`
3. Press `Enter`

### Start It:

```
sudo systemctl start fashion_ai
sudo systemctl enable fashion_ai
```

## Step 9: Final Test 🎉

1. Open browser
2. Go to `http://YOUR-IP` (without :8000 this time)
3. You should see the same success message!

## You Did It! 🎊

Your FashionModelingAI is now running on Google Cloud!

### Useful Commands for Later:

- Check if service is running: `sudo systemctl status fashion_ai`
- Restart service: `sudo systemctl restart fashion_ai`
- View logs: `sudo journalctl -u fashion_ai -f` (Ctrl+C to stop)
- Update code: `git pull`

### Need Help?

- Something broken? Check logs: `sudo journalctl -u fashion_ai -f`
- Web not working? Check nginx: `sudo systemctl status nginx`
- App not starting? Check configuration: `nano .env`