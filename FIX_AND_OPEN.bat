@echo off
REM we are good - fix and open script ready
color 0A
echo ========================================
echo   Career OS - Fix and Open
echo ========================================
echo.

REM Step 1: Update timestamps
echo [1/3] Updating file timestamps...
cd Backend
for /r %%f in (*.py *.json *.txt *.md) do (
    copy /b "%%f"+,, "%%f" >nul 2>&1
)
cd ..

cd Frontend  
for /r %%f in (*.html *.js *.css) do (
    copy /b "%%f"+,, "%%f" >nul 2>&1
)
cd ..

for %%f in (*.md *.txt *.bat *.html) do (
    copy /b "%%f"+,, "%%f" >nul 2>&1
)

echo    Done! All files updated to current time.
echo.

REM Step 2: Check backend
echo [2/3] Checking backend status...
curl -s http://127.0.0.1:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo    Backend is running! [OK]
) else (
    echo    Backend not detected. It should be running in background.
)
echo.

REM Step 3: Open application
echo [3/3] Opening Career OS Application...
start "" "%~dp0Frontend\index.html"
echo    Application opened!
echo.

echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Backend URL: http://127.0.0.1:8000
echo Frontend: Opened in browser
echo.
echo If frontend doesn't connect:
echo 1. Check backend: http://127.0.0.1:8000/health
echo 2. Refresh the browser page
echo.
echo Press any key to exit...
pause >nul
