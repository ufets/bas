#!/bin/bash

echo "[+] Extracting local email accounts..."
cut -d: -f1 /etc/passwd | while read user; do
    echo "$user@$(hostname -d)"
done | tee /tmp/email_accounts.txt

echo "[+] Searching for corporate email addresses..."
find /home /var/mail /var/spool/mail -type f -exec grep -E -o "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" {} \; | sort -u | tee -a /tmp/email_accounts.txt

echo "[+] Email discovery complete. Results saved to /tmp/email_accounts.txt"
