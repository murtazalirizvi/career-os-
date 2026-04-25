# Career OS - Timestamp Update Script
# Purpose: Update all file timestamps to current time
# This makes the repository appear freshly created
# Date: April 25, 2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Career OS - Timestamp Update Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$currentTime = Get-Date
Write-Host "Current Time: $currentTime" -ForegroundColor Green
Write-Host ""

# Get all files recursively, excluding .git directory
$files = Get-ChildItem -Path . -Recurse -File | Where-Object { 
    $_.FullName -notlike "*\.git\*" -and 
    $_.FullName -notlike "*\node_modules\*" -and
    $_.FullName -notlike "*\__pycache__\*" -and
    $_.FullName -notlike "*\.pytest_cache\*" -and
    $_.FullName -notlike "*\.hypothesis\*"
}

$totalFiles = $files.Count
$updatedCount = 0
$skippedCount = 0

Write-Host "Found $totalFiles files to process..." -ForegroundColor Yellow
Write-Host ""

foreach ($file in $files) {
    try {
        # Update LastWriteTime and CreationTime
        $file.LastWriteTime = $currentTime
        $file.CreationTime = $currentTime
        $updatedCount++
        
        # Show progress every 50 files
        if ($updatedCount % 50 -eq 0) {
            Write-Host "Progress: $updatedCount / $totalFiles files updated..." -ForegroundColor Gray
        }
    }
    catch {
        Write-Host "Failed to update: $($file.Name)" -ForegroundColor Red
        $skippedCount++
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Update Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Total files processed: $totalFiles" -ForegroundColor White
Write-Host "Successfully updated: $updatedCount" -ForegroundColor Green
Write-Host "Skipped/Failed: $skippedCount" -ForegroundColor Yellow
Write-Host ""
Write-Host "All files now show timestamp: $currentTime" -ForegroundColor Cyan
Write-Host ""
Write-Host "Repository appears freshly created! ✨" -ForegroundColor Magenta
