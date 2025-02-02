import requests
import sys
import json

def search_certificates(domain):
    try:
        url = f"https://crt.sh/?q={domain}&output=json"
        response = requests.get(url)

        if response.status_code == 200:
            certificates = response.json()

            # Записываем сырые данные в файл
            with open(f"{domain}_certificates.json", "w", encoding='utf-8') as file:
                json.dump(certificates, file, ensure_ascii=False, indent=4)

            subdomains = set()

            for cert in certificates:
                common_name = cert.get('common_name')

                # Печатаем найденные поддомены
                if common_name and domain in common_name:
                    subdomains.add(common_name)

            print("Найденные поддомены:")
            for subdomain in subdomains:
                print(subdomain)
        else:
            print(f"Error fetching certificates: {response.status_code}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <domain>")
    else:
        domain_to_search = sys.argv[1]
        search_certificates(domain_to_search)