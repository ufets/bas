$guidQuery = wmic product where "Name like 'Kaspersky Endpoint Security%'" get IdentifyingNumber
$guid = $guidQuery | Select-String -Pattern "\{[A-F0-9\-]+\}" | ForEach-Object { $_.Matches[0].Value }

if ($guidQuery -ne $null) {
    $msiexecCommand = "msiexec.exe /x $guid KLPLOGIN=*** KLPASSWD=*** /quiet"
    Start-Process -NoNewWindow -FilePath cmd -ArgumentList "/c $msiexecCommand"
    Write-Host $msiexecCommand
    $msiexecCommand2 = "msiexec.exe /x $guid /quiet"
    Start-Process -NoNewWindow -FilePath cmd -ArgumentList "/c $msiexecCommand2"
}