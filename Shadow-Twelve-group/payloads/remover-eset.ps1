$guidQuery = wmic product where "Name like 'ESET NOD32 Antivirus%'" get IdentifyingNumber |
Select-String -Pattern "\{[A-F0-9\-]+\}" | ForEach-Object { $_.Matches[0].Value }

if ($guidQuery -ne $null) {
    $msiexecCommand = "msiexec.exe /x $guidQuery /quiet /norestart"
    Start-Process -NoNewWindow -FilePath cmd -ArgumentList "/c $msiexecCommand"
}