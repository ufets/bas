# Email Discovery Script (Pentest version)
# Collects emails from AD, Outlook profiles and Exchange GAL
# Returns:
# - 0 exit code if emails found
# - 1 exit code if no emails found
# Outputs results to console

$foundEmails = [System.Collections.Generic.HashSet[string]]::new()

# 1. Active Directory Extraction
Write-Output "[+] Extracting email accounts from Active Directory..."
try {
    $adUsers = Get-ADUser -Filter * -Property EmailAddress -ErrorAction Stop | 
               Where-Object { $_.EmailAddress }
    
    if ($adUsers) {
        Write-Output "[AD] Found $($adUsers.Count) email(s):"
        foreach ($user in $adUsers) {
            Write-Output $user.EmailAddress
            $foundEmails.Add($user.EmailAddress) | Out-Null
        }
    }
    else {
        Write-Output "[AD] No email addresses found"
    }
}
catch {
    Write-Output "[AD] Error: $_"
}

# 2. Outlook Profiles Extraction
Write-Output "`n[+] Extracting emails from Outlook profiles..."
$outlookPaths = @('16.0', '15.0', '14.0') | ForEach-Object { 
    "HKCU:\Software\Microsoft\Office\$_\Outlook\Profiles" 
}

foreach ($path in $outlookPaths) {
    if (Test-Path $path) {
        Get-ChildItem $path | ForEach-Object {
            $profilePath = "$path\$($_.PSChildName)"
            $email = (Get-ItemProperty -Path $profilePath -Name "Email" -ErrorAction SilentlyContinue).Email
            if ($email) {
                Write-Output "[Outlook] Found in $($_.PSChildName): $email"
                $foundEmails.Add($email) | Out-Null
            }
        }
    }
}

# 3. Exchange Global Address List Extraction
Write-Output "`n[+] Attempting Global Address List extraction..."
try {
    # Try Exchange Online connection
    if (-not (Get-Command Get-GlobalAddressList -ErrorAction SilentlyContinue)) {
        Write-Output "[GAL] Trying to connect to Exchange Online..."
        Import-Module ExchangeOnlineManagement -ErrorAction SilentlyContinue
        Connect-ExchangeOnline -ErrorAction Stop -WarningAction SilentlyContinue
    }

    if (Get-Command Get-Recipient -ErrorAction SilentlyContinue) {
        Write-Output "[GAL] Querying Global Address List..."
        $galResults = Get-Recipient -ResultSize Unlimited -ErrorAction Stop | 
                      Where-Object PrimarySmtpAddress
        
        if ($galResults) {
            Write-Output "[GAL] Found $($galResults.Count) entries:"
            $galResults | ForEach-Object {
                Write-Output $_.PrimarySmtpAddress
                $foundEmails.Add($_.PrimarySmtpAddress) | Out-Null
            }
        }
        else {
            Write-Output "[GAL] No entries found"
        }
    }
}
catch {
    Write-Output "[GAL] Error: $_"
}
finally {
    if ((Get-PSSession | Where-Object ComputerName -like *.outlook.com)) {
        Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue
    }
}

# Results and exit code
Write-Output "`n[+] Discovery complete.`n"
Write-Output "======================"
Write-Output "Total unique emails found: $($foundEmails.Count)"
Write-Output "======================"

if ($foundEmails.Count -gt 0) {
    exit 0
}
else {
    exit 1
}