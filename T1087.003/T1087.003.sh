#!/bin/bash

# Directories to search
directories=("/var/mail" "/var/spool" "/var/log" "/home")

# Regular expression to find e-mails
email_regex="[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

# Found e-mails
found_emails=()

# Search in all specified directories
for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        emails=$(grep -Eroh "$email_regex" "$dir" 2>/dev/null | grep -v -E "mozilla\.org|mozilla\.com|\.service|ubuntu\.com|ubuntu\.org|redhat\.com" )
        if [ -n "$emails" ]; then
            found_emails+=($emails)
        fi
    else
        echo "Directory not found: $dir" >&2
    fi
done

# Remove duplicates
unique_emails=$(printf "%s\n" "${found_emails[@]}" | sort -u)

if [ -z "$unique_emails" ]; then
    echo "No e-mail addresses found."
    exit 2
else
    echo "Found e-mail addresses:"
    echo "$unique_emails"
fi