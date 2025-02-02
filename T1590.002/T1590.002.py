
import socket
import dns.resolver
import sys

def dns_lookup(target, record_type="A"):
    """Выполняет DNS-запрос и сохраняет результат в конфигурацию."""
    records = []
    try:
        if record_type == "PTR":
            try:
                ip_address = socket.gethostbyname(target)
            except socket.gaierror:
                print(f"Error resolving domain for PTR-record for {target}", "ERROR")
                return records

            try:
                addr = dns.resolver.resolve_address(ip_address)
                for rdata in addr:
                    records.append(str(rdata)) # Преобразование в строку
            except dns.resolver.NXDOMAIN:
                print(f"No PTR-record for {target}", "INFO")
            except dns.exception.DNSException as e:
                print(f"Error finding PTR-record for {target}", "ERROR")
        else:
            answers = dns.resolver.resolve(target, record_type)
            for rdata in answers:
                records.append(str(rdata)) # Преобразование в строку

    except dns.resolver.NoAnswer:
        print(f"No {record_type}-record for {target}", "INFO")
    except dns.resolver.NXDOMAIN:
        print(f"{target} does not exists", "ERROR")
    except dns.exception.DNSException as e:
        print(f"Error DNS-request for {target}", "ERROR")

    return records

def get_dns_records( target): # Явно указываем тип session
    """Выполняет DNS-запросы, ищет поддомены и обновляет БД."""
    record_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]
    original_ip = None


    for record in record_types:
        try:
            results = dns_lookup(target, record)
            print(f"DNS({record}) information for {target}: {results}", "INFO")
        except Exception as e:
            print(f"Error during DNS lookup for {record}: {e}", "INFO")    


def main():
    if len(sys.argv) != 2:
        print("Использование: python script.py <URL> <домен> <глубина>")
        print("Пример: python script.py mephi.ru")
        sys.exit(1)

    target = sys.argv[1]
    
    get_dns_records(target)


if __name__ == "__main__":
    main()