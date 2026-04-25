$css_path = 'styles.css'
$css = Get-Content $css_path -Raw
# Convert all pure white to Dark Teal (Milk)
$css = $css -replace 'rgba\(255, \s*255, \s*255,', 'rgba(0, 70, 67,'
$css = $css -replace 'rgba\(255,255,255,', 'rgba(0, 70, 67,'
$css = $css -replace '(?i)#ffffff', '#004643'
$css = $css -replace '(?i)#fff\b', '#004643'

# Convert old Indigo to Milk
$css = $css -replace 'rgba\(99, \s*102, \s*241,', 'rgba(0, 70, 67,'
$css = $css -replace 'rgba\(99,102,241,', 'rgba(0, 70, 67,'
$css = $css -replace 'rgba\(139, \s*92, \s*246,', 'rgba(0, 70, 67,'
$css = $css -replace 'rgba\(168, \s*85, \s*247,', 'rgba(0, 70, 67,'
$css = $css -replace 'rgba\(129, \s*140, \s*248,', 'rgba(0, 70, 67,'

# Dark backgrounds to Light Palm
$css = $css -replace 'rgba\(5, \s*5, \s*5,', 'rgba(0, 70, 67,'
$css = $css -replace 'rgba\(5,5,5,', 'rgba(0, 70, 67,'
$css = $css -replace 'rgba\(8, \s*8, \s*14,', 'rgba(240, 237, 229, 0.95'
$css = $css -replace 'rgba\(10, \s*10, \s*18,', 'rgba(240, 237, 229, 0.95'
$css = $css -replace 'rgba\(0, \s*0, \s*0, \s*0\.4\)', 'rgba(0, 70, 67, 0.05)'
$css = $css -replace 'rgba\(0, \s*0, \s*0, \s*0\.3\)', 'rgba(0, 70, 67, 0.04)'
$css = $css -replace 'rgba\(0, \s*0, \s*0, \s*0\.2\)', 'rgba(0, 70, 67, 0.03)'
$css = $css -replace 'rgba\(0,0,0,0\.4\)', 'rgba(0,70,67,0.05)'
$css = $css -replace 'rgba\(0,0,0,0\.3\)', 'rgba(0,70,67,0.04)'
$css = $css -replace 'rgba\(0,0,0,0\.2\)', 'rgba(0,70,67,0.03)'

# Make sure buttons have Palm text on Milk background
$css = $css -replace 'color:\s*#004643(.*?background:\s*var\(--accent-grad\))', 'color: var(--bg)$1'
$css = $css -replace '(background:\s*var\(--accent-grad\).*?)color:\s*#004643', '$1color: var(--bg)'

Set-Content $css_path -Value $css
Write-Output "styles.css updated for Light Theme."
