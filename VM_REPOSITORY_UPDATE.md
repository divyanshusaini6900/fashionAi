# VM Repository Update Guide

## Overview
This guide explains how to update your repository on the Google Cloud VM after pushing changes to GitHub.

## Prerequisites
- You have SSH access to your VM
- You have made changes to your local repository
- You have pushed changes to GitHub

## Update Process

### Step 1: Push Changes to GitHub (Local Machine)
First, make sure all your changes are pushed to GitHub:

```bash
# Add all changes
git add .

# Commit changes
git commit -m "Your commit message describing the changes"

# Push to GitHub
git push origin main
```

### Step 2: Connect to Your VM
SSH into your VM using one of these methods:

1. **Using Google Cloud Console:**
   - Go to Google Cloud Console
   - Navigate to Compute Engine → VM instances
   - Click the SSH button for your instance

2. **Using command line (if you have SSH keys set up):**
   ```bash
   ssh your-username@your-vm-external-ip
   ```

### Step 3: Navigate to Project Directory
Once connected to your VM, navigate to the project directory:

```bash
cd ~/fashionAi
```

### Step 4: Pull Latest Changes
Pull the latest changes from GitHub:

```bash
git pull origin main
```

If you're using a different branch, replace `main` with your branch name:
```bash
git pull origin your-branch-name
```

### Step 5: Handle Dependencies (If Needed)
If you've added new dependencies, install them:

```bash
# Activate virtual environment
source fash_env/bin/activate

# Install new dependencies
pip install -r requirements.txt
```

### Step 6: Restart the Service
After updating the code, restart your application service:

```bash
sudo systemctl restart fashion_ai
```

### Step 7: Verify the Update
Check that the service is running correctly:

```bash
# Check service status
sudo systemctl status fashion_ai

# Check application logs
sudo journalctl -u fashion_ai -f
```

Press `Ctrl+C` to stop viewing logs.

### Step 8: Test the Application
Test that your changes are working:

1. Open your browser and go to `http://YOUR-VM-IP`
2. Check the API documentation at `http://YOUR-VM-IP/docs`
3. Test any new endpoints or features you added

## Common Issues and Solutions

### Issue 1: Merge Conflicts
If you get merge conflicts:

```bash
# Check status
git status

# Manually resolve conflicts in the files shown
# Edit the files to resolve conflicts

# Add resolved files
git add .

# Complete the merge
git commit -m "Resolved merge conflicts"

# Restart service
sudo systemctl restart fashion_ai
```

### Issue 2: Permission Denied
If you get permission denied errors:

```bash
# Check file permissions
ls -la

# Fix permissions if needed
sudo chown -R $USER:$USER ~/fashionAi
```

### Issue 3: Service Won't Start After Update
If the service fails to start after updating:

```bash
# Check detailed logs
sudo journalctl -u fashion_ai --no-pager

# Check configuration files
cat .env

# Try starting manually to see errors
source fash_env/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Issue 4: Dependency Issues
If you get module not found errors:

```bash
# Activate virtual environment
source fash_env/bin/activate

# Install missing dependencies
pip install -r requirements.txt

# If that doesn't work, install specific package
pip install package-name
```

## Best Practices

### 1. Always Test Locally First
Before pushing to GitHub and updating the VM:
- Test your changes locally
- Ensure all tests pass
- Verify the application starts correctly

### 2. Use Version Control Best Practices
- Make small, focused commits
- Write descriptive commit messages
- Push frequently to avoid large merges

### 3. Backup Before Major Updates
For significant changes:
```bash
# Create a backup branch
git checkout -b backup-before-major-update
git checkout main
```

### 4. Monitor After Updates
After updating the VM:
- Check service status
- Monitor application logs
- Test critical functionality

## Quick Reference Commands

```bash
# On your local machine
git add .
git commit -m "Description of changes"
git push origin main

# On your VM
cd ~/fashionAi
git pull origin main
source fash_env/bin/activate
pip install -r requirements.txt
sudo systemctl restart fashion_ai
sudo systemctl status fashion_ai
```

## Rollback Process

If something goes wrong and you need to rollback:

### Option 1: Rollback to Previous Commit
```bash
# On VM, check commit history
git log --oneline

# Rollback to previous commit (replace COMMIT_HASH)
git reset --hard COMMIT_HASH

# Restart service
sudo systemctl restart fashion_ai
```

### Option 2: Use Backup Branch
```bash
# If you created a backup branch
git checkout backup-before-major-update
git branch -D main
git checkout -b main

# Restart service
sudo systemctl restart fashion_ai
```

## Verification Checklist

After updating your VM repository:
- [ ] Service is running (`sudo systemctl status fashion_ai`)
- [ ] Application is accessible via browser
- [ ] API documentation loads (`http://YOUR-VM-IP/docs`)
- [ ] New features work as expected
- [ ] No errors in logs (`sudo journalctl -u fashion_ai -f`)
- [ ] Performance is acceptable

## Troubleshooting Tips

1. **If git pull fails:**
   ```bash
   git fetch origin
   git reset --hard origin/main
   ```

2. **If service won't restart:**
   ```bash
   # Check for syntax errors
   source fash_env/bin/activate
   python -m py_compile app/main.py
   
   # Check configuration
   cat .env
   ```

3. **If dependencies are missing:**
   ```bash
   source fash_env/bin/activate
   pip list
   pip install -r requirements.txt
   ```

## Need Help?

If you continue to experience issues:

1. Check detailed logs:
   ```bash
   sudo journalctl -u fashion_ai --no-pager
   ```

2. Verify your configuration:
   ```bash
   cat .env
   ```

3. Test manual startup:
   ```bash
   source fash_env/bin/activate
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

Remember to always restart your service after making updates:
```bash
sudo systemctl restart fashion_ai
```