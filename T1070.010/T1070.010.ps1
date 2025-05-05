$url = "https://raw.githubusercontent.com/xmrig/xmrig/refs/heads/master/README.md"
$tempDir = $env:TEMP
$randomName = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 8 | ForEach-Object {[char]$_})
$downloadPath = "$tempDir\$randomName"
$destPaths = @("C:\Windows\Temp", "C:\Users\Public", "C:\Temp")

try {
    Invoke-WebRequest -Uri $url -OutFile $downloadPath -UseBasicParsing
} catch {
    Write-Host "Download failed"
    exit 1
}

foreach ($dest in $destPaths) {
    if (-not (Test-Path $dest)) {
        New-Item -ItemType Directory -Path $dest -Force
    }
    try {
        Copy-Item -Path $downloadPath -Destination "$dest\$randomName" -Force
    } catch {
        Write-Host "Copy to $dest failed"
        exit 1
    }
}

Remove-Item -Path $downloadPath -Force
foreach ($dest in $destPaths) {
    $fileToDelete = "$dest\$randomName"
    if (Test-Path $fileToDelete) {
        Remove-Item -Path $fileToDelete -Force
    }
}

Write-Host "All operations completed successfully"
exit 0