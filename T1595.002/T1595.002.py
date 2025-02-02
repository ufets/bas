import nmap
import sys

def vulnerability_scan(ip_file):
    nm = nmap.PortScanner()
    
    # Чтение IP-адресов из файла
    with open(ip_file, 'r') as file:
        ips = file.readlines()
    
    for ip in ips:
        ip = ip.strip()
        print(f"Сканирование уязвимостей для IP: {ip}")
        try:
            # Используем NSE для запуска скриптов уязвимостей
            nm.scan(ip, arguments='--script vuln')
            for host in nm.all_hosts():
                print(f"\nРезультаты для {host}:")
                if nm[host].all_tcp():
                    for port in nm[host]['tcp']:
                        if 'script' in nm[host]['tcp'][port]:
                            print(f"Порт {port} Уязвимости: {nm[host]['tcp'][port]['script']}")
        except Exception as e:
            print(f"Ошибка при сканировании {ip}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <ip_file>")
    else:
        vulnerability_scan(sys.argv[1])