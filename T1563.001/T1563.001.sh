#!/usr/bin/env bash
set -euo pipefail

# Заголовок таблицы
printf "%6s %8s %-30s %6s %7s %7s\n" \
  "PID" "USER" "SOCK" "PERMS" "ACCESS" "HIJACK"

# Функция для проверки сокета агента
check_agent_sock() {
  local sock=$1
  # статусы
  local ftype perms access hijack
  # тип и права
  read -r ftype perms <<<"$(stat -c "%F %a" "$sock" 2>/dev/null || echo "none 000")"
  # проверяем R/W
  if [[ -r $sock && -w $sock && $ftype == "socket" ]]; then
    access="yes"
    if SSH_AUTH_SOCK="$sock" ssh-add -l &>/dev/null; then
      hijack="yes"
    else
      hijack="no"
    fi
  else
    access="no"; hijack="no"
  fi
  printf "%6s %8s %-30s %6s %7s %7s\n" \
    "$pid" "$user" "$sock" "$perms" "$access" "$hijack"
}

# Основной цикл по процессам sshd
for pid_path in /proc/[0-9]*; do
  pid=${pid_path##*/}
  # фильтруем только дочерние sshd-сессии с ForwardAgent
  grep -q "^sshd$" "/proc/$pid/comm" 2>/dev/null || continue
  grep -q "sshd: .*@.*" "/proc/$pid/cmdline" 2>/dev/null || continue

  # извлекаем SSH_AUTH_SOCK из окружения
  sock=$(tr '\0' '\n' < "/proc/$pid/environ" 2>/dev/null \
         | awk -F= '$1=="SSH_AUTH_SOCK"{print $2}')
  [[ $sock == /tmp/ssh-* ]] || continue

  # узнаём владельца процесса
  uid=$(awk '/^Uid:/{print $2}' "/proc/$pid/status" 2>/dev/null)
  user=$(getent passwd "$uid" | cut -d: -f1 || echo "N/A")

  check_agent_sock "$sock"
done

echo
echo "== Проверка конфигурации SSH-демона =="
# вытягиваем эффективные параметры sshd
cfg=$(sshd -tT)
agentf=$(echo "$cfg" | awk '/^allowagentforwarding /{print $2}')
tcpf=$(echo   "$cfg" | awk '/^allowtcpforwarding /{print $2}')
tunnel=$(echo "$cfg" | awk '/^permittleTunnel /{print $2}')

printf "AllowAgentForwarding: %s\n" "$agentf"
printf "AllowTcpForwarding:   %s\n" "$tcpf"
printf "PermitTunnel:         %s\n" "$tunnel"

# Вывод вердикта
if [[ "$agentf" == "yes" && "$(grep -c ' yes$' <<<"$cfg")" -gt 0 ]]; then
  echo
  echo "POSSIBLE AGENT FORWARDING VULNERABILITY"
fi
