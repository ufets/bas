from utils.base_utils import log
import socket
import dns.resolver
from utils.subdomains import find_subdomains, add_subdomains

def dns_lookup(target, record_type="A"):
    """Выполняет DNS-запрос и сохраняет результат в конфигурацию."""
    records = []
    try:
        if record_type == "PTR":
            try:
                ip_address = socket.gethostbyname(target)
            except socket.gaierror:
                log(f"Error resolving domain for PTR-record for {target}", "ERROR")
                return records

            try:
                addr = dns.resolver.resolve_address(ip_address)
                for rdata in addr:
                    records.append(str(rdata)) # Преобразование в строку
            except dns.resolver.NXDOMAIN:
                log(f"No PTR-record for {target}", "INFO")
            except dns.exception.DNSException as e:
                log(f"Error finding PTR-record for {target}", "ERROR")
        else:
            answers = dns.resolver.resolve(target, record_type)
            for rdata in answers:
                records.append(str(rdata)) # Преобразование в строку

    except dns.resolver.NoAnswer:
        log(f"No {record_type}-record for {target}", "INFO")
    except dns.resolver.NXDOMAIN:
        log(f"{target} does not exists", "ERROR")
    except dns.exception.DNSException as e:
        log(f"Error DNS-request for {target}", "ERROR")

    return records

def get_dns_records(session, target): # Явно указываем тип session
    """Выполняет DNS-запросы, ищет поддомены и обновляет БД."""
    record_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]
    original_ip = None

    if target.domains:
        try:
            original_ip = dns_lookup(target.domains[0].name, "A")[0]
        except Exception as e:
            log(f"Error getting A record for original domain: {e}", "INFO")
            return

    for record in record_types:
        try:
            results = dns_lookup(target.domains[0].name, record)
            log(f"DNS({record}) information for {target}: {results}", "INFO")
            if results:
                subdomains = find_subdomains(results, target.domains[0].name)
                add_subdomains(session, subdomains, original_ip)
        except Exception as e:
            log(f"Error during DNS lookup for {record}: {e}", "INFO")    
        

    session.commit()