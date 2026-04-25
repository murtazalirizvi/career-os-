@echo off
echo Starting Career OS Project...
echo.
echo [1/2] Starting Backend Server...
cd /d "%~dp0Backend"
start "Backend Server" cmd /k "py -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/2] Starting Frontend Server...
cd /d "%~dp0Frontend"
start "Frontend Server" cmd /k "py serve.py"

echo.
echo ========================================
echo Career OS is now running!
echo ========================================
echo Frontend: http://localhost:5500
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to open the application in your browser...
pause > nul
start http://localhost:5500
echo.
echo Both servers are running in separate windows.
echo Close those windows to stop the servers.
pause
