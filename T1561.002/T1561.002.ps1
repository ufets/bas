# Function to check for administrative rights
Function Check-AdminRights {
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentUser.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)
}

# Function to check access to physical drive
Function Check-PhysicalDriveAccess {
    try {
        # Attempt to open a physical drive
        $device = [System.IO.File]::Open("\\.\PhysicalDrive0", 'Open', 'ReadWrite')
        $device.Close()
        return $true
    } catch {
        return $false
    }
}

# Check if BitLocker is enabled (an example of security software similar to SELinux controls)
Function Check-BitLockerStatus {
    $bitLockerStatus = Get-BitLockerVolume -MountPoint C: | Select-Object -ExpandProperty ProtectionStatus
    return $bitLockerStatus -eq 1
}

# Main logic
if (Check-AdminRights) {
    if (Check-PhysicalDriveAccess) {
        Write-Output "Sufficient rights to perform operations on the physical disk device."
        if (Check-BitLockerStatus) {
            Write-Output "BitLocker is enabled. Disk operations might be restricted."
            exit 1
        } else {
            Write-Output "BitLocker is not enabled."
            exit 0
        }
    } else {
        Write-Output "No access to the physical disk device."
        exit 2
    }
} else {
    Write-Output "No administrative rights. Insufficient rights to perform disk operations."
    exit 3
}