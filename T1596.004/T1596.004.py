import requests
import sys
import dns.resolver

def check_cdn(domain):
    try:
        url = f"http://{domain}"
        response = requests.get(url, timeout=5)
        headers = response.headers
        cdn_headers = {}

        # Общие CDN заголовки
        common_cdn_headers = ['Via', 'X-Cache', 'CF-Cache-Status', 'Fastly-Backend-Name', 'Server-Timing']
        
        for header in common_cdn_headers:
            if header in headers:
                cdn_headers[header] = headers[header]

        # Проверяем DNS-записи
        ip_addresses = []
        c_names = []

        try:
            a_records = dns.resolver.resolve(domain, 'A')
            ip_addresses = [ip.to_text() for ip in a_records]
        except Exception as a_e:
            print(f"Ошибка при запросе A-записей для {domain}: {a_e}")

        try:
            cname_records = dns.resolver.resolve(domain, 'CNAME')
            c_names = [cname.target.to_text() for cname in cname_records]
        except dns.resolver.NoAnswer:
            print(f"CNAME-запись для {domain} отсутствует.")
        except Exception as cname_e:
            print(f"Ошибка при запросе CNAME-записей для {domain}: {cname_e}")

        if cdn_headers or c_names or ip_addresses:
            print(f"CDN информация для {domain}:")
            if cdn_headers:
                print("HTTP-заголовки указывающие на CDN:")
                for header, value in cdn_headers.items():
                    print(f"{header}: {value}")

            if c_names:
                print("\nCNAME-записи:")
                for cname in c_names:
                    print(cname)
                
            if ip_addresses:
                print("\nIP-адреса:")
                for ip in ip_addresses:
                    print(ip)
        else:
            print(f"Нет явной CDN информации для {domain}.")
            
    except Exception as e:
        print(f"Ошибка при запросе {domain}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python cdn_check.py <domain>")
    else:
        domain_to_check = sys.argv[1]
        check_cdn(domain_to_check)