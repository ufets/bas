import dns.resolver
import sys

def search_dns(domain):
    try:
        # Поиск A-записей (основные IP адреса)
        a_records = dns.resolver.resolve(domain, 'A')
        print(f"A-записи для {domain}:")
        for ip in a_records:
            print(ip.to_text())

        # Поиск MX-записей (серверы почты)
        mx_records = dns.resolver.resolve(domain, 'MX')
        print(f"\nMX-записи (почтовые серверы) для {domain}:")
        for mx in mx_records:
            print(mx.to_text())

        # Поиск NS-записей (name серверы)
        ns_records = dns.resolver.resolve(domain, 'NS')
        print(f"\nNS-записи для {domain}:")
        for ns in ns_records:
            print(ns.to_text())

        # Поиск CNAME-записей (каноническое имя)

        # Поиск TXT-записей (текстовые записи)
        txt_records = dns.resolver.resolve(domain, 'TXT')
        print(f"\nTXT-записи для {domain}:")
        for txt in txt_records:
            print(txt.to_text())

        cname_records = dns.resolver.resolve(domain, 'CNAME')
        print(f"\nCNAME-записи для {domain}:")
        for cname in cname_records:
            print(cname.to_text())

    except Exception as e:
        print(f"Ошибка при поиске DNS для {domain}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python dns_search.py <domain>")
    else:
        search_dns(sys.argv[1])