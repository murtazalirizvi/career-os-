# Career-OS GitHub Push Script (PowerShell)
# This script will push your project to GitHub

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Career-OS GitHub Push Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Git is installed
try {
    $gitVersion = git --version 2>&1
    Write-Host "[OK] Git is installed: $gitVersion" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "[ERROR] Git is not installed or not in PATH!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Git for Windows from:" -ForegroundColor Yellow
    Write-Host "https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "After installation, restart your terminal and run this script again." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if already a git repository
if (Test-Path ".git") {
    Write-Host "[INFO] Git repository already initialized" -ForegroundColor Yellow
} else {
    Write-Host "[STEP 1] Initializing Git repository..." -ForegroundColor Cyan
    git init
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to initialize Git repository" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "[OK] Git repository initialized" -ForegroundColor Green
}
Write-Host ""

# Check if user is configured
try {
    $userName = git config user.name 2>&1
    if ([string]::IsNullOrEmpty($userName)) {
        throw "User not configured"
    }
} catch {
    Write-Host "[WARNING] Git user not configured" -ForegroundColor Yellow
    Write-Host "Please configure Git with your name and email:" -ForegroundColor Yellow
    Write-Host ""
    $username = Read-Host "Enter your name"
    $useremail = Read-Host "Enter your email"
    git config --global user.name "$username"
    git config --global user.email "$useremail"
    Write-Host "[OK] Git user configured" -ForegroundColor Green
    Write-Host ""
}

# Add all files
Write-Host "[STEP 2] Adding files to Git..." -ForegroundColor Cyan
git add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to add files" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "[OK] Files added" -ForegroundColor Green
Write-Host ""

# Show status
Write-Host "[INFO] Files to be committed:" -ForegroundColor Cyan
git status --short
Write-Host ""

# Create commit
Write-Host "[STEP 3] Creating commit..." -ForegroundColor Cyan
git commit -m "Initial commit: Career-OS project with all 5 features"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARNING] Commit failed or no changes to commit" -ForegroundColor Yellow
    Write-Host "This might be okay if you've already committed these files" -ForegroundColor Yellow
}
Write-Host ""

# Check if remote exists
try {
    $remoteUrl = git remote get-url origin 2>&1
    Write-Host "[INFO] Remote already exists: $remoteUrl" -ForegroundColor Yellow
} catch {
    Write-Host "[STEP 4] Adding GitHub remote..." -ForegroundColor Cyan
    git remote add origin https://github.com/murtazalirizvi/career-os-.git
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to add remote" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "[OK] Remote added" -ForegroundColor Green
}
Write-Host ""

# Set main branch
Write-Host "[STEP 5] Setting main branch..." -ForegroundColor Cyan
git branch -M main
Write-Host "[OK] Main branch set" -ForegroundColor Green
Write-Host ""

# Push to GitHub
Write-Host "[STEP 6] Pushing to GitHub..." -ForegroundColor Cyan
Write-Host ""
Write-Host "[INFO] You may be prompted for GitHub credentials" -ForegroundColor Yellow
Write-Host "       Use your GitHub username and Personal Access Token" -ForegroundColor Yellow
Write-Host "       (Not your password - tokens are required now)" -ForegroundColor Yellow
Write-Host ""
Write-Host "       Generate token at: https://github.com/settings/tokens" -ForegroundColor Yellow
Write-Host ""

git push -u origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[WARNING] Push failed. This might be because:" -ForegroundColor Yellow
    Write-Host "  1. Repository already has content" -ForegroundColor Yellow
    Write-Host "  2. Authentication failed" -ForegroundColor Yellow
    Write-Host "  3. Network issues" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Trying to pull first..." -ForegroundColor Cyan
    git pull origin main --allow-unrelated-histories
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Pull successful, trying push again..." -ForegroundColor Green
        git push -u origin main
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] Push still failed" -ForegroundColor Red
            Write-Host "Please check your credentials and try manually" -ForegroundColor Yellow
            Read-Host "Press Enter to exit"
            exit 1
        }
    } else {
        Write-Host "[ERROR] Pull failed" -ForegroundColor Red
        Write-Host "Please resolve conflicts manually" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "[SUCCESS] Project pushed to GitHub!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your project is now available at:" -ForegroundColor Cyan
Write-Host "https://github.com/murtazalirizvi/career-os-" -ForegroundColor Cyan
Write-Host ""
Write-Host "To make future updates:" -ForegroundColor Yellow
Write-Host "  1. Make your changes" -ForegroundColor Yellow
Write-Host "  2. Run: git add ." -ForegroundColor Yellow
Write-Host "  3. Run: git commit -m 'Your message'" -ForegroundColor Yellow
Write-Host "  4. Run: git push" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit"
