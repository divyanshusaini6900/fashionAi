# Deployment Guide: FashionModelingAI on AWS EC2

This guide walks through deploying the FashionModelingAI application on an AWS EC2 instance, setting up Nginx as a reverse proxy, and configuring the environment for production use.

## Table of Contents

- [Prerequisites](#prerequisites)
- [1. AWS Setup](#1-aws-setup)
- [2. Server Configuration](#2-server-configuration)
- [3. Application Deployment](#3-application-deployment)
- [4. Nginx Configuration](#4-nginx-configuration)
- [5. Running the Application](#5-running-the-application)
- [6. Setting Up SSL (Optional)](#6-setting-up-ssl-optional)
- [7. Troubleshooting](#7-troubleshooting)

## Prerequisites

Before starting, ensure you have:

- An AWS account with access to EC2 and S3 services
- Your application's AWS credentials (Access Key ID and Secret Access Key)
- Your OpenAI and Replicate API keys
- Basic familiarity with Linux commands and SSH

## 1. AWS Setup

### Launch EC2 Instance

1. Go to AWS EC2 Console and click "Launch Instance"
2. Configure the instance:

   ```
   Name: fashion-ai-server
   AMI: Ubuntu Server 22.04 LTS
   Instance Type: t2.micro (or larger based on needs)
   Key Pair: Create new
   Network Settings: Allow HTTP (80), HTTPS (443), and SSH (22)
   ```

3. Create and download your key pair (`.pem` file)
4. Launch the instance

### Configure Security Group

Ensure your security group has these inbound rules:

- SSH (Port 22) from your IP
- HTTP (Port 80) from anywhere
- HTTPS (Port 443) from anywhere

### Set Up IAM Role (Best Practice)

1. Go to IAM Console → Roles → Create Role
2. Select AWS Service → EC2
3. Add permissions:
   - AmazonS3FullAccess (or create custom policy)
4. Name the role (e.g., `EC2-S3-Access-Role`)
5. Attach role to your EC2 instance:
   - EC2 Dashboard → Select Instance
   - Actions → Security → Modify IAM Role
   - Select your new role

## 2. Server Configuration

### Connect to Your Instance

```bash
# Change permissions of your key file
chmod 400 path/to/your-key.pem

# SSH into your instance
ssh -i path/to/your-key.pem ubuntu@your-instance-ip
```

### Install Required Software

```bash
# Update package lists
sudo apt update
sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3-pip python3-venv nginx -y

# Install system dependencies
sudo apt install build-essential libssl-dev libffi-dev python3-dev -y
```

## 3. Application Deployment

### Clone Repository and Set Up Environment

```bash
# Clone your repository
git clone https://github.com/your-username/FashionModelingAI.git
cd FashionModelingAI

# Create and activate virtual environment
python3 -m venv fash_env
source fash_env/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

### Create Environment File

Create `.env` file in the project root:

```bash
nano .env
```

Add your environment variables:

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

## 4. Nginx Configuration

### Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/fashion_ai
```

Add this configuration:

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

    # Increase max upload size
    client_max_body_size 10M;
}
```

Enable the configuration:

```bash
sudo ln -s /etc/nginx/sites-available/fashion_ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 5. Running the Application

### Create Systemd Service

Create a service file:

```bash
sudo nano /etc/systemd/system/fashion_ai.service
```

Add this configuration:

```ini
[Unit]
Description=Fashion AI FastAPI Application
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/FashionModelingAI
Environment="PATH=/home/ubuntu/FashionModelingAI/fash_env/bin"
EnvironmentFile=/home/ubuntu/FashionModelingAI/.env
ExecStart=/home/ubuntu/FashionModelingAI/fash_env/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app -b 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl start fashion_ai
sudo systemctl enable fashion_ai
sudo systemctl status fashion_ai
```

## 6. Setting Up SSL (Optional)

Install Certbot and get SSL certificate:

```bash
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
sudo certbot --nginx
```

Follow the prompts to configure HTTPS.

## 7. Troubleshooting

### Check Application Logs

```bash
sudo journalctl -u fashion_ai -f
```

### Check Nginx Logs

```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Common Issues

1. **502 Bad Gateway**

   - Check if Gunicorn is running
   - Verify Nginx configuration
   - Check application logs for errors

2. **Permission Issues**

   - Ensure proper file permissions
   - Check ownership of directories

3. **Environment Variables**

   - Verify .env file exists and has correct permissions
   - Check if systemd service loads environment variables

4. **S3 Access Issues**
   - Verify IAM role permissions
   - Check AWS credentials
   - Ensure proper bucket policy

### Maintenance Commands

```bash
# Restart application
sudo systemctl restart fashion_ai

# Check application status
sudo systemctl status fashion_ai

# View logs
sudo journalctl -u fashion_ai -f

# Restart Nginx
sudo systemctl restart nginx
```

## Security Notes

1. Keep your `.env` file secure and never commit it to version control
2. Regularly update your system packages
3. Use strong passwords and keep your SSH key secure
4. Consider implementing rate limiting in Nginx
5. Monitor your AWS CloudWatch logs and metrics

## Monitoring

Consider setting up:

1. AWS CloudWatch for metrics and logs
2. Server monitoring (CPU, memory, disk usage)
3. Application performance monitoring
4. Error tracking service

Remember to regularly:

- Backup your data
- Update your dependencies
- Monitor your AWS costs
- Check your logs for unusual activity
