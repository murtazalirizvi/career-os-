@echo off
REM we are good - app launcher script ready
echo ========================================
echo   Opening Career OS Application
echo ========================================
echo.
echo Backend Status: Running on port 8000
echo Opening Frontend...
echo.

REM Open the frontend directly
start "" "%~dp0Frontend\index.html"

echo.
echo Application opened in your default browser!
echo.
echo If it doesn't work, manually open:
echo %~dp0Frontend\index.html
echo.
pause
