#!/bin/bash

function check_disk_permissions {
    local disk=$1

    echo -e "\e[36mTesting Disk: $disk\e[0m"
    echo "Checking user permissions for $disk..."
    ls -l "$disk" | awk '{print "Permissions:", $1, "Owner:", $3, "Group:", $4}'
    if [[ $(id -u) -ne 0 ]]; then
        echo -e "\e[33mNote: You are not root. Some operations may be restricted.\e[0m"
    fi

    # Проверяем открытие для записи
    if ! (exec 3>"$disk"); then
        echo -e "\e[31mError: Cannot open $disk for writing. Permission denied.\e[0m"
        return 1
    fi
    exec 3>&-

    # Проверяем запись через dd
    echo "Testing write access on $disk without root..."
    if dd if=/dev/zero of="$disk" bs=512 count=1 oflag=direct status=none 2>/dev/null; then
        echo -e "\e[32mSuccess: $disk is writable without root.\e[0m"
        return 0
    else
        echo -e "\e[31mError: Write access to $disk is denied.\e[0m"
        return 1
    fi
}

function get_physical_disks {
    lsblk -d -n -o NAME | awk '{print "/dev/" $1}'
}

disks=$(get_physical_disks)
if [[ -z "$disks" ]]; then
    echo -e "\e[31mNo physical disks found.\e[0m"
    exit 1
fi

# Флаг, указывающий, что хотя бы на одном диске запись успешна
any_success=1  # по умолчанию — неуспех

for disk in $disks; do
    if check_disk_permissions "$disk"; then
        any_success=0
        # Можно выходить сразу, но здесь проверяем все диски
    fi
    echo
done

exit $any_success
