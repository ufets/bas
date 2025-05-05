$HostFle = "C:\Users\Public\Temp\hosts.txt"
$OutputFile = "C:\Users\Public\Temp\res.txt"
$hostnames = Get-Content $HostFle
$null = New-Item -Path $HostFle -ItemType File -Force

foreach ($hostname in $hostnames) {
    $users = Get-ChildItem "\\$hostname\c$\Users" -ErrorAction SilentlyContinue | 
    Where-Object { $_.PSIsContainer} 

    foreach ($user in $users) {
        $userPath = "\\$hostname\c$\Users\$($user.Name)"
        $tdataPath = "$userPath\AppData\Roaming\Telegram Desktop\tdata"
        $hasTdata = Test-Path $tdataPath

        if ($hasTdata) {
            $result = "hostname: $hostname, user: $($user.Name)`ntdataPath: $tdataPath"
            Write-Output $result
            Add-Content -Path $OutputFile -Value $result
        }
    }
}