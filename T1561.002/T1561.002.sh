#!/bin/bash

# Проверка прав суперпользователя
if [ "$EUID" -ne 0 ]; then
    echo "Нет прав суперпользователя. Выполнение Disk Structure Wipe будет невозможно."
    exit 2
fi

echo "Запущено с правами суперпользователя."

# Проверка наличия необходимых утилит
tools=("dd" "parted" "wipefs")
available_tools=()

for tool in "${tools[@]}"; do
    if command -v $tool &> /dev/null; then
        available_tools+=($tool)
    fi
done

if [ ${#available_tools[@]} -gt 0 ]; then
    echo "Доступные утилиты для работы с диском: ${available_tools[@]}"
    echo "В теории, возможно выполнить Disk Structure Wipe."
    exit 0
else
    echo "Нет доступных утилит для работы с диском. Disk Structure Wipe маловероятен."
    exit 1
fi