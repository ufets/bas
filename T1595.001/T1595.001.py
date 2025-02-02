import nmap
import sys

def scan_ip_blocks(ip_file):
    nm = nmap.PortScanner()
    
    # Чтение IP-адресов из файла
    with open(ip_file, 'r') as file:
        ips = file.readlines()
    
    for ip in ips:
        ip = ip.strip()
        print(f"Сканирование IP: {ip}")
        try:
            nm.scan(ip, arguments='-sP')  # Используем '-sP' для пингового сканирования
            for host in nm.all_hosts():
                print(f"Хост {host} обнаружен")
        except Exception as e:
            print(f"Ошибка при сканировании {ip}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <ip_file>")
    else:
        scan_ip_blocks(sys.argv[1])