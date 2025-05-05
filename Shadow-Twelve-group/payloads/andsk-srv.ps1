[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$tempDir = "$env:TEMP\AnyDeskTemp"; $exePath = "$tempDir\AnyDesk.exe"; $serviceName = "AnyDeskService"

try {
    # Скачивание и установка
    New-Item -Path $tempDir -ItemType Directory -Force
    Invoke-WebRequest "https://download.anydesk.com/AnyDesk.exe" -OutFile $exePath
    
    Start-Process -FilePath $exePath -ArgumentList "--install service --silent" -Wait
    Start-Service -Name $serviceName -ErrorAction Stop
    
    # Проверка установки
    if (Get-Service $serviceName -ErrorAction SilentlyContinue) {
        Write-Host "[SUCCESS] Service installed and running" -ForegroundColor Green
    }
}
catch {
    Write-Host "[ERROR] Installation failed: $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    # Очистка
    try {
        if (Get-Service $serviceName -ErrorAction SilentlyContinue) {
            Stop-Service -Name $serviceName -Force
            sc.exe delete $serviceName | Out-Null
        }
        
        if (Test-Path $exePath) {
            Remove-Item -Path $exePath -Force
        }
        
        if (Test-Path $tempDir) {
            Remove-Item -Path $tempDir -Recurse -Force
        }
        
        Write-Host "[CLEANUP] All artifacts removed" -ForegroundColor Yellow
    }
    catch {
        Write-Host "[CLEANUP ERROR] $($_.Exception.Message)" -ForegroundColor DarkRed
    }
}