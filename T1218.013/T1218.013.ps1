param (
    [int]$targetPid,     # Target process ID (renamed from pid to avoid conflict)
    [string]$dllPath     # Path to the DLL to be injected
)

# Check if the process exists by the target PID
$process = Get-Process -Id $targetPid -ErrorAction SilentlyContinue
if (-not $process) {
    Write-Host "Error: Process with PID $targetPid not found."
    exit 1
}

# Check if the DLL exists
if (-not (Test-Path $dllPath)) {
    Write-Host "Error: DLL file $dllPath not found."
    exit 1
}

# Execute mavinject to inject the DLL into the target process
$cmd = "C:\Windows\System32\mavinject.exe $targetPid /INJECTDLL $dllPath"
Write-Host "Executing command: $cmd"
Invoke-Expression $cmd

Write-Host "DLL successfully injected into process $targetPid."
