# Функция для проверки прав доступа и записи на диск
function Test-DiskWriteAccess {
    param (
        [string]$Disk
    )

    Write-Host "Testing Disk: $Disk" -ForegroundColor Cyan

    # Проверка доступности устройства для записи
    try {
        $stream = New-Object IO.FileStream($Disk, 'Open', 'ReadWrite')
        Write-Host "Success: $Disk is accessible for read and write." -ForegroundColor Green
        $stream.Close()
    } catch {
        Write-Host "Error: Cannot open $Disk for writing. Permission denied." -ForegroundColor Red
        return
    }

    # Попытка записи случайных данных
    try {
        $randomData = [byte[]](0..255 | ForEach-Object { Get-Random -Maximum 256 })
        $stream = New-Object IO.FileStream($Disk, 'Open', 'ReadWrite')
        $stream.Seek(0, [System.IO.SeekOrigin]::Begin) | Out-Null
        $stream.Write($randomData, 0, $randomData.Length)
        $stream.Close()
        Write-Host "Success: Write access to $Disk was successfully tested." -ForegroundColor Green
    } catch {
        Write-Host "Error: Write access to $Disk is denied." -ForegroundColor Red
    }
}

# Функция для получения списка физических дисков
function Get-PhysicalDisks {
    $disks = Get-WmiObject -Class Win32_DiskDrive
    return $disks
}

# Основная логика
$disks = Get-PhysicalDisks
if ($disks.Count -eq 0) {
    Write-Host "No physical disks found." -ForegroundColor Red
    exit 1
}

foreach ($disk in $disks) {
    $diskPath = "\\.\PhysicalDrive$($disk.DeviceID)"
    Test-DiskWriteAccess -Disk $diskPath
    Write-Host
}
