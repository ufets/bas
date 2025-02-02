import whois
import sys

def search_whois(domain):
    try:
        domain_info = whois.whois(domain)
        print(f"Информация WHOIS для {domain}:")
        print(f"Регистратор: {domain_info.registrar}")
        print(f"Дата окончания регистрации: {domain_info.expiration_date}")
        print(f"Дата создания: {domain_info.creation_date}")
        print(f"Дата обновления: {domain_info.updated_date}")
        print(f"DNS-серверы: {domain_info.name_servers}")

        # Проверяем наличие email, так как он может быть недоступен
        contact_emails = domain_info.emails
        if contact_emails:
            print("Контакты:")
            for email in contact_emails:
                print(f" - {email}")

    except Exception as e:
        print(f"Ошибка при запросе WHOIS для {domain}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python whois_search.py <domain>")
    else:
        search_whois(sys.argv[1])