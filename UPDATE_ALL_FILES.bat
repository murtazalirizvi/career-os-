@echo off
echo ========================================
echo   Updating All File Timestamps
echo ========================================
echo.

REM Update Backend files
echo Updating Backend files...
cd Backend
for /r %%f in (*) do (
    copy /b "%%f"+,, "%%f" >nul 2>&1
)
cd ..

REM Update Frontend files
echo Updating Frontend files...
cd Frontend
for /r %%f in (*) do (
    copy /b "%%f"+,, "%%f" >nul 2>&1
)
cd ..

REM Update root files
echo Updating root files...
for %%f in (*) do (
    copy /b "%%f"+,, "%%f" >nul 2>&1
)

echo.
echo ========================================
echo   All Files Updated!
echo ========================================
echo.
echo Press any key to continue...
pause >nul
