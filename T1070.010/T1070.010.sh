#!/usr/bin/env bash
set -e

URL="https://raw.githubusercontent.com/xmrig/xmrig/refs/heads/master/README.md"
DOWNLOAD_DIR="."
RANDOM_NAME=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 8)
DOWNLOAD_PATH="$DOWNLOAD_DIR/$RANDOM_NAME"
DEST_DIRS=("/tmp" "/dev/shm" "/var/tmp")

mkdir -p "$DOWNLOAD_DIR" "${DEST_DIRS[@]}"
if ! curl -sSL "$URL" -o "$DOWNLOAD_PATH"; then
    echo "Download failed"
    exit 1
fi

for dir in "${DEST_DIRS[@]}"; do
    mkdir -p "$dir"
    if ! cp -f "$DOWNLOAD_PATH" "$dir/$RANDOM_NAME"; then
        echo "Copy to $dir failed"
        exit 1
    fi
done

rm -f "$DOWNLOAD_PATH"
for dir in "${DEST_DIRS[@]}"; do
    rm -f "$dir/$RANDOM_NAME"
done

echo "All operations completed successfully"
exit 0