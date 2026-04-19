# 🚀 Push Your Project to GitHub

## Step 1: Install Git for Windows

### Download and Install Git

1. **Download Git**:
   - Visit: https://git-scm.com/download/win
   - Click "Click here to download" for the latest version
   - Or direct link: https://github.com/git-for-windows/git/releases/latest

2. **Run the Installer**:
   - Double-click the downloaded `.exe` file
   - Click "Next" through the setup wizard
   - **IMPORTANT**: On "Adjusting your PATH environment" screen, select:
     - ✅ **"Git from the command line and also from 3rd-party software"**
   - Keep all other default settings
   - Click "Install"

3. **Verify Installation**:
   - **Close and reopen** your terminal/PowerShell/IDE
   - Run: `git --version`
   - You should see something like: `git version 2.x.x`

---

## Step 2: Configure Git (First Time Only)

Open a new terminal and run these commands:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Replace with your actual name and email (use the same email as your GitHub account).

---

## Step 3: Initialize Git Repository

Navigate to your project folder:

```bash
cd "C:\Users\Lenovo\Downloads\Career_OS_Project_Analysis -murtaza\Career_OS_Project_Analysis"
```

Or if you're already in the project folder, just run:

```bash
git init
```

---

## Step 4: Add Files to Git

Add all files to staging:

```bash
git add .
```

Check what will be committed:

```bash
git status
```

---

## Step 5: Create First Commit

```bash
git commit -m "Initial commit: Career-OS project with all 5 features"
```

---

## Step 6: Connect to GitHub

Add your GitHub repository as remote:

```bash
git remote add origin https://github.com/murtazalirizvi/career-os-.git
```

Set the main branch:

```bash
git branch -M main
```

---

## Step 7: Push to GitHub

### Option A: If Repository is Empty

```bash
git push -u origin main
```

### Option B: If Repository Has Content

If the repository already has files, you'll need to pull first:

```bash
git pull origin main --allow-unrelated-histories
```

Then push:

```bash
git push -u origin main
```

---

## 🔐 Authentication

When you push, GitHub will ask for authentication:

### Option 1: Personal Access Token (Recommended)

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name: "Career-OS Project"
4. Select scopes: ✅ **repo** (all sub-options)
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)
7. When prompted for password, paste the token

### Option 2: GitHub CLI

Install GitHub CLI and authenticate:

```bash
# Download from: https://cli.github.com/
gh auth login
```

---

## 📝 Complete Command Sequence

Here's the complete sequence to copy and paste:

```bash
# Navigate to project folder
cd "C:\Users\Lenovo\Downloads\Career_OS_Project_Analysis -murtaza\Career_OS_Project_Analysis"

# Initialize git
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: Career-OS project with all 5 features"

# Add remote repository
git remote add origin https://github.com/murtazalirizvi/career-os-.git

# Set main branch
git branch -M main

# Push to GitHub
git push -u origin main
```

---

## 🔄 Future Updates

After the initial push, to update your repository:

```bash
# Check status
git status

# Add changed files
git add .

# Commit changes
git commit -m "Description of your changes"

# Push to GitHub
git push
```

---

## ❌ Troubleshooting

### Error: "git is not recognized"

**Solution**: Git is not installed or not in PATH
- Install Git from https://git-scm.com/download/win
- **Restart your terminal/IDE** after installation
- Verify with: `git --version`

### Error: "fatal: not a git repository"

**Solution**: You're not in the project folder or haven't initialized git
```bash
cd "C:\Users\Lenovo\Downloads\Career_OS_Project_Analysis -murtaza\Career_OS_Project_Analysis"
git init
```

### Error: "remote origin already exists"

**Solution**: Remove and re-add the remote
```bash
git remote remove origin
git remote add origin https://github.com/murtazalirizvi/career-os-.git
```

### Error: "failed to push some refs"

**Solution**: Pull first, then push
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Error: "Authentication failed"

**Solution**: Use a Personal Access Token instead of password
- Generate token at: https://github.com/settings/tokens
- Use token as password when prompted

### Error: "Permission denied"

**Solution**: Check repository URL and your access rights
```bash
git remote -v  # Check current remote
git remote set-url origin https://github.com/murtazalirizvi/career-os-.git
```

---

## 📊 Verify Your Push

After pushing, verify on GitHub:

1. Visit: https://github.com/murtazalirizvi/career-os-
2. You should see all your files
3. Check the commit history
4. Verify README.md is displayed

---

## 🎯 Quick Reference

### Check Status
```bash
git status
```

### View Commit History
```bash
git log --oneline
```

### View Remote URL
```bash
git remote -v
```

### Pull Latest Changes
```bash
git pull
```

### Push Changes
```bash
git push
```

### Create New Branch
```bash
git checkout -b feature-name
```

### Switch Branch
```bash
git checkout main
```

---

## 📞 Need Help?

If you encounter issues:

1. Check the error message carefully
2. Look in the Troubleshooting section above
3. Verify Git is installed: `git --version`
4. Ensure you're in the correct directory: `pwd` or `cd`
5. Check your GitHub repository exists and you have access

---

## ✅ Success Checklist

- [ ] Git installed and verified (`git --version`)
- [ ] Git configured (name and email)
- [ ] Repository initialized (`git init`)
- [ ] Files added (`git add .`)
- [ ] First commit created (`git commit`)
- [ ] Remote added (`git remote add origin`)
- [ ] Pushed to GitHub (`git push -u origin main`)
- [ ] Verified on GitHub website

---

**Once complete, your project will be live at:**
https://github.com/murtazalirizvi/career-os-

🎉 **Good luck!**
