Write-Output "[+] Extracting email accounts from Active Directory..."

# Получение списка email-адресов пользователей AD
$emails = Get-ADUser -Filter * -Property EmailAddress | Select-Object -ExpandProperty EmailAddress
$emails | Out-File -FilePath C:\Temp\email_accounts.txt

Write-Output "[+] Extracting emails from Outlook profiles..."

# Поиск email-аккаунтов в Outlook (если установлен)
if (Test-Path "HKCU:\Software\Microsoft\Office\16.0\Outlook\Profiles") {
    $profiles = Get-ChildItem "HKCU:\Software\Microsoft\Office\16.0\Outlook\Profiles"
    foreach ($profile in $profiles) {
        $email = Get-ItemProperty -Path "HKCU:\Software\Microsoft\Office\16.0\Outlook\Profiles\$profile" -Name Email
        if ($email) {
            Write-Output "Found: $email"
            Add-Content C:\Temp\email_accounts.txt $email
        }
    }
}

Write-Output "[+] Email discovery complete. Results saved to C:\Temp\email_accounts.txt"
