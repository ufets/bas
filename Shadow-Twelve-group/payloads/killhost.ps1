$computers = Get-Content -Path "C:\adminhost.txt"

while ($true) {
    Invoke-Command -ComputerName $computers -ScriptBlock { Stop-Computer -Force -Confirm:$false }
    Start-Sleep -Seconds 60
}