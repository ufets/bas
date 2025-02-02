import nmap
import sys

def scan_software_info(target_ip):
    nm = nmap.PortScanner()
    nm.scan(target_ip, arguments='-sV')

    for host in nm.all_hosts():
        print(f'Хост: {host}')
        if 'tcp' in nm[host]:
            for port in nm[host]['tcp']:
                proto_info = nm[host]['tcp'][port]
                print(f"Порт {port}: {proto_info.get('name', 'unknown')} {proto_info.get('version', 'unknown')}")
        
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <ip_address>")
    else:
        scan_software_info(sys.argv[1])