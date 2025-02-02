import nmap
from models import Port
from utils.base_utils import log

def scan_ports(ip_address):
    log(f"Starting scan for {ip_address}")
    nm = nmap.PortScanner()
    nm.scan(ip_address, arguments='-sS -sV --top-ports 30')  # Добавляем -sV для определения версии

    port_data = []
    for proto in nm[ip_address].all_protocols():
        lport = nm[ip_address][proto].keys()
        for port in lport:
            state = nm[ip_address][proto][port]['state']
            service = nm[ip_address][proto][port]['name']
            version = nm[ip_address][proto][port].get('version', '')
            info = f"{service} {version}".strip()  # Формируем комбинированное поле
            port_data.append((port, proto, state, info))
    return port_data

def scan_vulnerabilities(ip_address):
    log(f"Starting vulnerability scan for {ip_address}, please wait...")
    nm = nmap.PortScanner()
    nm.scan(ip_address, arguments='--script vuln')
    return nm[ip_address]  # Получаем результаты сканирования

def check_open_ports(session, target):
    all_ports_data = scan_ports(target.ip_address)
    log(f"Ports data: {all_ports_data}")
    for port_number, protocol, state, info in all_ports_data:
        if not session.query(Port).filter_by(ip_id=target.id, port_number=port_number, protocol=protocol).first():
            Port.create(session, ip=target, port_number=port_number, protocol=protocol, state=state, info=info)

    session.close()

