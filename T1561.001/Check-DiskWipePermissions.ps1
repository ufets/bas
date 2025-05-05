# Функция проверки прав и записи на диск
function Test-DiskWriteAccess {
    param (
        [string]$Disk
    )

    Write-Host "Testing Disk: $Disk" -ForegroundColor Cyan

    try {
        $stream = [IO.File]::Open($Disk, 'Open', 'ReadWrite')
        Write-Host "Success: $Disk is accessible for read and write." -ForegroundColor Green
        $stream.Close()
        return $true
    } catch {
        Write-Host "Error: Cannot open $Disk for writing. Permission denied." -ForegroundColor Red
        return $false
    }
}

# Основная логика
$disks = Get-WmiObject -Class Win32_DiskDrive
if (-not $disks) {
    Write-Host "No physical disks found." -ForegroundColor Red
    exit 1
}

# Булев флаг для агрегирования результатов
$anySuccess = $false

foreach ($disk in $disks) {
    # Формируем путь к физическому устройству
    $path = "\\.\PhysicalDrive$($disk.Index)"
    if (Test-DiskWriteAccess -Disk $path) {
        $anySuccess = $true
    }
    Write-Host
}

# Выход с кодом 0, если была хотя бы одна успешная проверка, иначе 1
if ($anySuccess) {
    exit 0
} else {
    exit 1
}
