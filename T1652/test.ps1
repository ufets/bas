# Функция для получения информации о версии файла (как и прежде)
function Get-FileVersion {
    param(
        [string]$Path
    )

    try {
        if (!(Test-Path $Path)) {
            Write-Warning "File not found: $Path"
            return $null
        }

        $FileVersionInfo = Get-Item $Path | Get-ItemProperty | Select-Object -ExpandProperty VersionInfo

        if ($FileVersionInfo) {
            [PSCustomObject]@{
                FileName    = $Path
                ProductName = $FileVersionInfo.ProductName
                FileVersion = $FileVersionInfo.FileVersion
                Company     = $FileVersionInfo.CompanyName
                Description = $FileVersionInfo.FileDescription
            }
        } else {
            Write-Warning "Version information not available for: $Path"
            return $null
        }
    }
    catch {
        Write-Error "Error getting version information for $Path : ${$_.Exception.Message}"
        return $null
    }
}

# Путь к выходному файлу
$OutputFile = "driver_info.txt"

# Получаем список драйверов
$Drivers = Get-WmiObject Win32_SystemDriver | Where-Object {$_.State -eq "Running"}

# Создаем массив для результатов
$Results = @()

# Перебираем драйверы
foreach ($Driver in $Drivers) {
    $DriverPath = $Driver.PathName

    if ($DriverPath) {
        $VersionInfo = Get-FileVersion $DriverPath

        if ($VersionInfo) {
            $Results += $VersionInfo
        } else {
            $Results += [PSCustomObject]@{
                FileName = $DriverPath
                Error    = "Failed to retrieve version information."
            }
        }
    } else {
        $Results += [PSCustomObject]@{
            Name  = $Driver.Name
            Error = "Driver path not defined."
        }
        Write-Warning "Driver path not defined for: $($Driver.Name)"
    }
}

# Запись в текстовый файл
$Results | ForEach-Object {
    $OutputString = ""
    if ($_.FileName) {
        $OutputString += "File Name: $($_.FileName)`r`n"
    }
    if ($_.ProductName) {
        $OutputString += "Product Name: $($_.ProductName)`r`n"
    }
    if ($_.FileVersion) {
        $OutputString += "File Version: $($_.FileVersion)`r`n"
    }
    if ($_.Company) {
        $OutputString += "Company: $($_.Company)`r`n"
    }
        if ($_.Description) {
        $OutputString += "Description: $($_.Description)`r`n"
    }
    if ($_.Error) {
        $OutputString += "Error: $($_.Error)`r`n"
    }
    $OutputString += "`r`n" # Пустая строка между драйверами

    $OutputString | Out-File $OutputFile -Encoding UTF8 -Append
}

Write-Host "Driver information written to file: $OutputFile"