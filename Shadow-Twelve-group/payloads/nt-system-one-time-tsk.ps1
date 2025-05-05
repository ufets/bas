$taskName = "OneTimeTask-NT-SYSTEM"
$action   = 'cmd.exe /c whoami > C:\Temp\whoami.txt & schtasks /delete /tn OneTimeTask /f'

schtasks /create /tn $taskName /tr $action /sc once /st (Get-Date).AddMinutes(1).ToString('HH:mm') `
           /rl highest /ru SYSTEM /f
Start-Sleep 70
type C:\Temp\whoami.txt;
del C:\Temp\whoami.txt;