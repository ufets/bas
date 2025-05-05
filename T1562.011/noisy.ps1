# Настройки
$Duration = 900  # 15 минут
$MaliciousDomains = @("ngrok.io", "anydesk.com", "localtonet.com", "gsocket.io")
$TempPath = "C:\Windows\Temp\"
$Ports = @(80, 443, 22, 8080)  # Целевые порты

# Модуль 1: TCP-соединения
$TcpNoiseJob = {
    $domains = $using:MaliciousDomains
    $ports = $using:Ports
    $startTime = Get-Date
    
    while ((New-TimeSpan -Start $startTime).TotalSeconds -lt $using:Duration) {
        foreach ($domain in $domains) {
            foreach ($port in $ports) {
                try {
                    # Установка и немедленное закрытие TCP-соединения
                    $tcpClient = New-Object System.Net.Sockets.TcpClient
                    $tcpClient.Connect($domain, $port)
                    $tcpClient.Close()
                } catch {}
            }
        }
        Start-Sleep -Seconds 3
    }
}

# Модуль 2: Файловая активность
$FileNoiseJob = {
    $startTime = Get-Date
    while ((New-TimeSpan -Start $startTime).TotalSeconds -lt $using:Duration) {
        1..50 | ForEach-Object {
            $randName = "susp_file_$(Get-Date -Format 'yyyyMMddHHmmss')_$((Get-Random -Maximum 9999)).tmp"
            New-Item -Path (Join-Path $using:TempPath $randName) -ItemType File -Force | Out-Null
        }
        Start-Sleep -Seconds 5
    }
}

# Модуль 3: Процессы
$ProcessNoiseJob = {
    $startTime = Get-Date
    while ((New-TimeSpan -Start $startTime).TotalSeconds -lt $using:Duration) {
        try {
            $proc = Start-Process notepad -PassThru -WindowStyle Hidden
            Start-Sleep -Seconds 2
            $proc | Stop-Process -Force -ErrorAction SilentlyContinue
        } catch {}
        Start-Sleep -Seconds 10
    }
}

# Запуск
$jobs = @(
    Start-Job -ScriptBlock $TcpNoiseJob
    Start-Job -ScriptBlock $FileNoiseJob
    Start-Job -ScriptBlock $ProcessNoiseJob
)
Start-Sleep -Seconds $Duration
$jobs | Stop-Job -PassThru | Remove-Job