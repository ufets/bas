#!/usr/bin/env bash
# Проверка возможности записи в логи Linux (без модификации)
# Выводит «Запись возможна» или «Запись невозможна» и возвращает код 0/1.

LOGFILES=(
  /var/log/syslog
  /var/log/messages
  /var/log/auth.log
  /var/log/daemon.log
  /var/log/kern.log
  /var/log/ufw.log
)

for f in "${LOGFILES[@]}"; do
  if [ -e "$f" ] && [ -w "$f" ]; then
    echo "Success: you can write to logs"
    exit 0
  fi
done

echo "Unable to write: Permission denied"
exit 1

