#!/bin/bash

# Функция для вывода информации о модулях ядра (драйверах) в Linux
list_kernel_modules() {
  echo "--- Kernel Modules (Drivers) ---"
  lsmod | column -t # Вывод списка загруженных модулей с форматированием
  echo ""

  # Дополнительная информация о каждом модуле
  for module in $(lsmod | awk '{print $1}' | tail -n +2); do # Исключаем заголовок
    echo "--- Information about module: $module ---"
    modinfo "$module"
    echo ""
  done
}

# Функция для вывода информации об устройствах в /dev
list_devices() {
  echo "--- Devices in /dev ---"
  ls -l /dev | less # Вывод списка устройств с постраничным просмотром (для больших списков)
  echo ""
}

# Функция для вывода информации о PCI устройствах (часто связаны с драйверами)
list_pci_devices() {
  echo "--- PCI Devices ---"
  lspci -vnn | less # Подробный вывод PCI устройств
  echo ""
}

# Функция для вывода информации о USB устройствах (часто связаны с драйверами)
list_usb_devices() {
  echo "--- USB Devices ---"
  lsusb -v | less # Подробный вывод USB устройств
  echo ""
}

# Главная функция
main() {
  echo "--- Device Driver and Hardware Information ---"
  echo ""

  list_kernel_modules
  list_devices
  list_pci_devices
  list_usb_devices

  # Дополнительные команды
  echo "--- System Information (uname) ---"
  uname -a
  echo ""
  echo "--- Hardware Information (lshw) ---" # Требуется установка: sudo apt install lshw
  lshw -short | less
    echo ""
    echo "--- CPU Information (lscpu) ---"
    lscpu | less
    echo ""
    echo "--- Memory Information (free -h) ---"
    free -h
    echo ""
    echo "--- Block Devices (lsblk) ---"
    lsblk
    echo ""
}

main

exit 0