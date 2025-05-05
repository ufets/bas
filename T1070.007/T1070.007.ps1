# Check for write permission to system logs (no actual writes)
# Outputs "Write permitted" or "Write not permitted" and returns exit code 0/1.

# Paths to check
$files = @(
    "C:\Windows\System32\LogFiles\Firewall\pfirewall.log",
    "C:\Windows\System32\winevt\Logs\Security.evtx",
    "C:\Windows\System32\winevt\Logs\System.evtx"
)

function Test-WritePermission {
    param([string]$Path)
    try {
        # Try opening for write and immediately close
        [System.IO.File]::OpenWrite($Path).Close()
        return $true
    } catch {
        return $false
    }
}

# 1. Ensure running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent() `
).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Output "Write not permitted: Administrator privileges required"
    exit 1
}

# 2. Check each file for write permission
foreach ($f in $files) {
    if (Test-Path $f -PathType Leaf -ErrorAction SilentlyContinue) {
        if (Test-WritePermission $f) {
            Write-Output "Write permitted"
            exit 0
        }
    }
}

# 3. None were writable
Write-Output "Write not permitted"
exit 1
