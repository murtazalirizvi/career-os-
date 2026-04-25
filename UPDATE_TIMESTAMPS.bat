@echo off
echo ========================================
echo Career OS - Timestamp Update Script
echo ========================================
echo.
echo Updating all file timestamps...
echo.

powershell -Command "Get-ChildItem -Path . -Recurse -File | Where-Object { $_.FullName -notlike '*\.git\*' -and $_.FullName -notlike '*\node_modules\*' -and $_.FullName -notlike '*\__pycache__\*' -and $_.FullName -notlike '*\.pytest_cache\*' } | ForEach-Object { $_.LastWriteTime = Get-Date; $_.CreationTime = Get-Date; Write-Host \"Updated: $($_.Name)\" -ForegroundColor Gray }"

echo.
echo ========================================
echo Update Complete!
echo ========================================
echo All files now show current timestamp
echo Repository appears freshly created!
echo.
pause
