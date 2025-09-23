# Nginx Troubleshooting Guide

## Problem: Application Only Works on Port 8000, Not on Standard HTTP Port

If your application is accessible at `http://YOUR-IP:8000` but not at `http://YOUR-IP`, it means Nginx is not properly configured or not running.

## Quick Fix Commands

First, let's check the status of all services:

```bash
# Check if your application service is running
sudo systemctl status fashion_ai

# Check if Nginx is running
sudo systemctl status nginx

# Test Nginx configuration
sudo nginx -t
```

## Solution Steps

### Step 1: Verify Nginx Configuration

1. Check your Nginx configuration file:
```bash
sudo nano /etc/nginx/sites-available/fashion_ai
```

Make sure it looks exactly like this (replace `your-username` with your actual username):
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

2. Save and exit (Ctrl+X, Y, Enter)

### Step 2: Ensure Nginx Configuration is Enabled

```bash
# Remove default site if it exists
sudo rm -f /etc/nginx/sites-enabled/default

# Enable your configuration
sudo ln -sf /etc/nginx/sites-available/fashion_ai /etc/nginx/sites-enabled/

# Test the configuration
sudo nginx -t
```

You should see:
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### Step 3: Restart Services

```bash
# Restart Nginx
sudo systemctl restart nginx

# Restart your application
sudo systemctl restart fashion_ai

# Check status of both services
sudo systemctl status nginx
sudo systemctl status fashion_ai
```

### Step 4: Check Firewall Settings

Make sure your firewall allows HTTP traffic:
```bash
# Check if UFW is active
sudo ufw status

# If needed, allow HTTP traffic
sudo ufw allow 80/tcp
```

### Step 5: Verify Your IP Address

Make sure you're using the correct external IP address:
1. Go to Google Cloud Console
2. Navigate to Compute Engine → VM instances
3. Find your instance and confirm the external IP address

## Common Issues and Solutions

### Issue 1: "Address already in use" error
This happens when another service is using port 80.

```bash
# Check what's using port 80
sudo lsof -i :80

# Kill the process if needed (replace PID with actual process ID)
sudo kill PID
```

### Issue 2: Nginx configuration test fails
```bash
# Check for syntax errors
sudo nginx -t

# Common fixes:
# 1. Make sure all braces {} are properly closed
# 2. Make sure all semicolons ; are present
# 3. Make sure file paths are correct
```

### Issue 3: Permission denied errors
```bash
# Check file permissions
ls -la /etc/nginx/sites-available/fashion_ai
ls -la /home/your-username/fashionAi/generated_files/

# Fix permissions if needed
sudo chmod 644 /etc/nginx/sites-available/fashion_ai
```

### Issue 4: Service won't start
```bash
# Check detailed logs
sudo journalctl -u nginx -f
sudo journalctl -u fashion_ai -f
```

## Testing Your Fix

After applying the fixes:

1. Test with curl:
```bash
curl http://localhost
```

2. Open your browser and go to:
```
http://YOUR-IP-ADDRESS
```

You should see the same response as when you go to:
```
http://YOUR-IP-ADDRESS:8000
```

## If Still Not Working

1. Check Nginx error logs:
```bash
sudo tail -f /var/log/nginx/error.log
```

2. Check your application logs:
```bash
sudo journalctl -u fashion_ai -f
```

3. Restart everything:
```bash
sudo systemctl restart fashion_ai
sudo systemctl restart nginx
```

## Final Verification

Once it's working, you should be able to access:
- API documentation: `http://YOUR-IP-ADDRESS/docs`
- Health check: `http://YOUR-IP-ADDRESS`
- Both should show the same content as `http://YOUR-IP-ADDRESS:8000`

If you continue to have issues, try a complete restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart fashion_ai
sudo systemctl restart nginx
```