# Essential GCP Deployment - Just the Most Important Steps

## 1. Google Cloud Setup (Do This First!)

### Create Project
1. Go to `console.cloud.google.com`
2. Click project dropdown → "New Project"
3. Name: `fashion-ai-project`
4. Click "Create"

### Enable Billing
1. Click "Billing" in left menu
2. Add your credit card

## 2. Create Your Cloud Computer

### Create VM Instance
1. Search "Compute Engine" → Click it
2. Click "VM instances" → "Create Instance"
3. Settings:
   - Name: `fashion-ai-server`
   - Region: `us-central1`
   - Machine type: `e2-medium`
   - Boot disk: `Ubuntu 22.04 LTS`
   - Check "Allow HTTP traffic"
4. Click "Create"

### Connect to VM
1. Wait for green checkmark
2. Click "SSH" button
3. Terminal window opens!

## 3. Install Software (Copy These Exactly)

In the terminal window, copy and paste these commands one by one:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required software
sudo apt install python3-pip python3-venv nginx -y
sudo apt install build-essential libssl-dev libffi-dev python3-dev -y

# Download your app
git clone https://github.com/your-username/FashionModelingAI.git
cd FashionModelingAI

# Set up Python environment
python3 -m venv fash_env
source fash_env/bin/activate

# Install Python packages
pip install -r requirements.txt
pip install gunicorn
```

## 4. Configure Your App

Create configuration file:
```bash
nano .env
```

Paste this (replace with YOUR real keys):
```env
OPENAI_API_KEY="your-real-openai-key"
REPLICATE_API_TOKEN="your-real-replicate-key"
GEMINI_API_KEY="your-real-gemini-key"
USE_LOCAL_STORAGE="true"
LOCAL_BASE_URL="http://localhost:8000"
```

Save it:
1. Press `Ctrl + X`
2. Press `Y`
3. Press `Enter`

## 5. Test It Works

Run the app:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Check it:
1. Find your VM's External IP in Google Cloud Console
2. Open new browser tab
3. Go to `http://YOUR-IP:8000`
4. You should see success message!

Stop the app: Press `Ctrl + C`

## 6. Make It Run Forever

Set up web server:
```bash
sudo nano /etc/nginx/sites-available/fashion_ai
```

Paste this:
```nginx
server {
    listen 80;
    server_name your-domain-or-ip;

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

Save it (Ctrl+X, Y, Enter), then run:
```bash
sudo ln -s /etc/nginx/sites-available/fashion_ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Create service file:
```bash
sudo nano /etc/systemd/system/fashion_ai.service
```

Paste this (replace "your-username" with actual username):
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

Save it (Ctrl+X, Y, Enter), then run:
```bash
sudo systemctl start fashion_ai
sudo systemctl enable fashion_ai
```

## 7. Final Test

1. Open browser
2. Go to `http://YOUR-IP` (without :8000)
3. You should see the same success message!

## You're Done! 🎉

Your FashionModelingAI is now running on Google Cloud Platform!

### Quick Commands for Later:
- Check status: `sudo systemctl status fashion_ai`
- Restart app: `sudo systemctl restart fashion_ai`
- View logs: `sudo journalctl -u fashion_ai -f`
- Update code: `git pull` then `sudo systemctl restart fashion_ai`