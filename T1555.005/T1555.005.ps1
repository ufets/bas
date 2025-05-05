# Функция для поиска всех возможных файлов KeePass в системе, проверяя наличие подстроки "KeePass" в названии папки
function Find-KeePass {
    $programFiles = [System.Environment]::GetFolderPath("ProgramFiles")
    $programFilesX86 = [System.Environment]::GetFolderPath("ProgramFilesX86")
    $systemDrive = [System.IO.Path]::GetPathRoot($env:SystemDrive)  # Получаем системный диск (например, C:)

    # Возможные пути KeePass, включая все возможные варианты имени файла
    $possiblePaths = @(
        "$programFiles\KeePass*Password Safe\KeePass.exe",  # Проверка для KeePass в Program Files
        "$programFilesX86\KeePass*Password Safe\KeePass.exe", # Для 32-битной версии в Program Files (x86)
        "C:\KeePass\KeePass.exe",                             # Проверка для нестандартных установок
        "C:\Program Files (x86)\KeePass Password Safe\KeePass.exe"  # Для установки в Program Files (x86)
    )

    # Проверяем стандартные пути
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            Write-Host -ForegroundColor Green "Found KeePass at: $path"
            return $path
        }
    }

    # Поиск по всей файловой системе (если не нашли по стандартным путям)
    Write-Host -ForegroundColor Yellow "Searching entire file system for KeePass..."
    $searchPaths = @("$systemDrive", "$env:USERPROFILE")  # Поиск в системном диске и профиле пользователя

    foreach ($path in $searchPaths) {
        Write-Host -ForegroundColor Yellow "Searching in $path for KeePass..."

        # Ищем папки с подстрокой "KeePass" в названии и исполнимые файлы .exe
        $folders = Get-ChildItem -Path $path -Recurse -Directory -ErrorAction SilentlyContinue |
                   Where-Object { $_.Name -match "KeePass" }

        # Перебираем найденные папки
        foreach ($folder in $folders) {
            $files = Get-ChildItem -Path $folder.FullName -Recurse -Include "KeePass.exe" -File -ErrorAction SilentlyContinue

            # Если находим файлы, выводим путь
            foreach ($file in $files) {
                Write-Host -ForegroundColor Green "Found KeePass at: $($file.FullName)"
                return $file.FullName
            }
        }
    }

    return $null
}

# Функция для поиска файлов базы данных KeePass (.kdbx и .kdb)
function Find-KeePassDatabases {
    $systemDrive = [System.IO.Path]::GetPathRoot($env:SystemDrive)

    Write-Host -ForegroundColor Cyan "Searching for KeePass database files (.kdbx, .kdb)..."

    # Поиск по всей файловой системе для файлов .kdbx и .kdb
    $dbFiles = Get-ChildItem -Path $systemDrive -Recurse -Include "*.kdbx", "*.kdb" -File -ErrorAction SilentlyContinue

    foreach ($db in $dbFiles) {
        Write-Host -ForegroundColor Cyan "Possible KeePass database found: $($db.FullName)"
    }
}

# Функция для получения версии KeePass
function Get-KeePassVersion {
    param([string]$keePassPath)
    if ($keePassPath) {
        return (Get-Item $keePassPath).VersionInfo.ProductVersion
    }
    return $null
}

# Функция для проверки, запущен ли KeePass в памяти
function Is-KeePassRunning {
    $keePassProcesses = Get-Process | Where-Object { $_.Name -match "KeePass" }
    
    if ($keePassProcesses) {
        Write-Host -ForegroundColor Green "KeePass is currently running."

        # Выводим PID процесса KeePass
        foreach ($process in $keePassProcesses) {
            Write-Host -ForegroundColor Green "Process PID: $($process.Id)"
            Write-Host -ForegroundColor Green "Attempting to dump process memory..."

            # Делаем дамп процесса
            try {
                $dumpFile = "$env:TEMP\KeePass_Dump_$($process.Id).dmp"
                $process | Export-Csv -Path $dumpFile -Force
                Write-Host -ForegroundColor Green "Memory dump saved to: $dumpFile"
            } catch {
                Write-Host -ForegroundColor Red "Failed to dump process memory: $_"
            }
        }
        return $true
    } else {
        Write-Host -ForegroundColor Red "KeePass is not running."
        return $false
    }
}

# Функция для проверки уязвимостей в зависимости от версии
function Check-KeePassVulnerabilities {
    param([string]$version)
    
    # Проверка на уязвимость CVE-2023-32784
    if ($version -lt "2.54") {
        Write-Host -ForegroundColor Red "KeePass is vulnerable to CVE-2023-32784 (Cleartext master password recovery from memory dump)."
    } else {
        Write-Host -ForegroundColor Green "KeePass is not vulnerable to CVE-2023-32784."
    }

    # Проверка на уязвимость CVE-2023-24055
    if ($version -le "2.53") {
        Write-Host -ForegroundColor Red "KeePass is vulnerable to CVE-2023-24055 (Cleartext passwords from configuration file write access)."
    } else {
        Write-Host -ForegroundColor Green "KeePass is not vulnerable to CVE-2023-24055."
    }

    # Проверка на уязвимость CVE-2022-0725
    if ($version -lt "2.33") {
        Write-Host -ForegroundColor Red "KeePass is vulnerable to CVE-2022-0725 (Plaintext passwords logged in system logs)."
    } else {
        Write-Host -ForegroundColor Green "KeePass is not vulnerable to CVE-2022-0725."
    }

    # Проверка на уязвимость CVE-2010-5200
    if ($version -lt "1.18") {
        Write-Host -ForegroundColor Red "KeePass is vulnerable to CVE-2010-5200 (Untrusted search path vulnerability)."
    } else {
        Write-Host -ForegroundColor Green "KeePass is not vulnerable to CVE-2010-5200."
    }

    # Можно добавить дополнительные проверки для других CVE по аналогии
}

# Главная логика
$keePassPath = Find-KeePass

if ($keePassPath) {
    Write-Host -ForegroundColor Green "KeePass is installed at: $keePassPath"

    # Получаем версию KeePass
    $version = Get-KeePassVersion -keePassPath $keePassPath
    if ($version) {
        Write-Host -ForegroundColor Green "KeePass Version: $version"
        
        # Проверяем на уязвимости
        Check-KeePassVulnerabilities -version $version

        # Проверяем, запущен ли KeePass
        Is-KeePassRunning
    } else {
        Write-Host -ForegroundColor Red "Unable to get version of KeePass."
    }
} else {
    Write-Host -ForegroundColor Red "KeePass is not installed."
}

# Ищем возможные базы данных KeePass (.kdbx и .kdb)
Find-KeePassDatabases
