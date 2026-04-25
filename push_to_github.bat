@echo off
REM we are good - GitHub push script ready
REM Career-OS GitHub Push Script
REM This script will push your project to GitHub

echo ========================================
echo Career-OS GitHub Push Script
echo ========================================
echo.

REM Check if Git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed or not in PATH!
    echo.
    echo Please install Git for Windows from:
    echo https://git-scm.com/download/win
    echo.
    echo After installation, restart your terminal and run this script again.
    echo.
    pause
    exit /b 1
)

echo [OK] Git is installed
echo.

REM Check if already a git repository
if exist ".git" (
    echo [INFO] Git repository already initialized
) else (
    echo [STEP 1] Initializing Git repository...
    git init
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to initialize Git repository
        pause
        exit /b 1
    )
    echo [OK] Git repository initialized
)
echo.

REM Check if user is configured
git config user.name >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Git user not configured
    echo Please configure Git with your name and email:
    echo.
    set /p username="Enter your name: "
    set /p useremail="Enter your email: "
    git config --global user.name "%username%"
    git config --global user.email "%useremail%"
    echo [OK] Git user configured
    echo.
)

REM Add all files
echo [STEP 2] Adding files to Git...
git add .
if %errorlevel% neq 0 (
    echo [ERROR] Failed to add files
    pause
    exit /b 1
)
echo [OK] Files added
echo.

REM Show status
echo [INFO] Files to be committed:
git status --short
echo.

REM Create commit
echo [STEP 3] Creating commit...
git commit -m "Initial commit: Career-OS project with all 5 features"
if %errorlevel% neq 0 (
    echo [WARNING] Commit failed or no changes to commit
    echo This might be okay if you've already committed these files
)
echo.

REM Check if remote exists
git remote get-url origin >nul 2>&1
if %errorlevel% neq 0 (
    echo [STEP 4] Adding GitHub remote...
    git remote add origin https://github.com/murtazalirizvi/career-os-.git
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to add remote
        pause
        exit /b 1
    )
    echo [OK] Remote added
) else (
    echo [INFO] Remote already exists
)
echo.

REM Set main branch
echo [STEP 5] Setting main branch...
git branch -M main
echo [OK] Main branch set
echo.

REM Push to GitHub
echo [STEP 6] Pushing to GitHub...
echo.
echo [INFO] You may be prompted for GitHub credentials
echo        Use your GitHub username and Personal Access Token
echo        (Not your password - tokens are required now)
echo.
echo        Generate token at: https://github.com/settings/tokens
echo.

git push -u origin main
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Push failed. This might be because:
    echo   1. Repository already has content
    echo   2. Authentication failed
    echo   3. Network issues
    echo.
    echo Trying to pull first...
    git pull origin main --allow-unrelated-histories
    if %errorlevel% equ 0 (
        echo [OK] Pull successful, trying push again...
        git push -u origin main
        if %errorlevel% neq 0 (
            echo [ERROR] Push still failed
            echo Please check your credentials and try manually
            pause
            exit /b 1
        )
    ) else (
        echo [ERROR] Pull failed
        echo Please resolve conflicts manually
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo [SUCCESS] Project pushed to GitHub!
echo ========================================
echo.
echo Your project is now available at:
echo https://github.com/murtazalirizvi/career-os-
echo.
echo To make future updates:
echo   1. Make your changes
echo   2. Run: git add .
echo   3. Run: git commit -m "Your message"
echo   4. Run: git push
echo.
pause
