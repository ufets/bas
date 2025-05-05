#!/bin/bash
check_ccache_files_access() {
    search_dirs=("/tmp" "/home")

    for dir in "${search_dirs[@]}"; do
        find "$dir" -type f -name 'krb5cc_*' 2>/dev/null | while read -r file; do
            if [ -r "$file" ] && [ -w "$file" ]; then
                echo "SUCCESS: $file"
            fi
        done
    done
}

check_ccache_files_access