# we are good - timestamp update script ready
# Update all file timestamps to current time
Write-Host "Updating file timestamps..." -ForegroundColor Green

# Update Backend files
Get-ChildItem -Path "Backend" -Recurse -File | ForEach-Object { 
    $_.LastWriteTime = Get-Date 
}

# Update Frontend files
Get-ChildItem -Path "Frontend" -Recurse -File | ForEach-Object { 
    $_.LastWriteTime = Get-Date 
}

# Update root files
Get-ChildItem -Path "." -File | ForEach-Object { 
    $_.LastWriteTime = Get-Date 
}

# Update documentation files
Get-ChildItem -Path "." -Filter "*.md" -File | ForEach-Object { 
    $_.LastWriteTime = Get-Date 
}

Write-Host "All file timestamps updated!" -ForegroundColor Green
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
