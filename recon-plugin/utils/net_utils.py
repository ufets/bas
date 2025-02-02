import socket
import requests
from utils.base_utils import format_datetime
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Функция для парсинга WHOIS данных
def parse_whois_info(whois_data):
    parsed_data = {
        "domain_name": whois_data.get("domain_name"),
        "registrar": whois_data.get("registrar"),
        "whois_server": whois_data.get("whois_server"),
        "referral_url": whois_data.get("referral_url"),
        "updated_date": format_datetime(whois_data.get("updated_date")),
        "creation_date": format_datetime(whois_data.get("creation_date")),
        "expiration_date": format_datetime(whois_data.get("expiration_date")),
        "name_servers": whois_data.get("name_servers"),
        "status": whois_data.get("status"),
        "emails": whois_data.get("emails"),
        "dnssec": whois_data.get("dnssec"),
        "org": whois_data.get("org"),
        "address": whois_data.get("address"),
        "city": whois_data.get("city"),
        "state": whois_data.get("state"),
        "zipcode": whois_data.get("zipcode"),
        "country": whois_data.get("country"),
        "ip_addresses": whois_data.get("ips")
    }
    return parsed_data



def extract_domains_with_subdomains(file_path):
    try:
        # Загружаем JSON из файла
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Проверяем наличие секции "dns"
        if "dns" not in data:
            raise ValueError("The JSON file does not contain a 'dns' section.")
        
        dns_section = data["dns"]
        domains = set()

        # Регулярное выражение для поиска доменных имен
        domain_regex = re.compile(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b')

        # Проходим по всем записям в "dns"
        for record_type, records in dns_section.items():
            for domain, values in records.items():
                domains.add(domain)  # Добавляем сам домен
                
                # Проверяем значения (списки строк) на доменные имена
                for value in values:
                    # Извлекаем домены из строк
                    found_domains = domain_regex.findall(value) if isinstance(value, str) else []
                    domains.update(found_domains)  # Добавляем найденные домены
        
        return list(domains)  # Преобразуем множество в список
    
    except Exception as e:
        print(f"Error: {e}")
        return []

def get_base_domain(domain):
    """Извлекает базовый домен (домен второго уровня)."""
    parts = domain.split(".")
    if len(parts) >= 2:
        return ".".join(parts[-2:])
    return None
    
def extract_domains_from_website(url, target, include_subdomains=True):
    """Извлекает домены из HTML-контента веб-страницы."""
    try:
        response = requests.get(url, timeout=10) # Добавим таймаут для предотвращения зависания
        response.raise_for_status()  # Проверяем код ответа HTTP (например, 200 OK)
        soup = BeautifulSoup(response.content, "html.parser")

        domains = set()

        # Поиск в атрибутах href тегов <a>
        for link in soup.find_all("a"):
            href = link.get("href")
            if href:
                parsed_url = urlparse(href)
                if parsed_url.netloc: # Проверяем, есть ли netloc (сетевое расположение)
                    domain = parsed_url.netloc
                    if target == get_base_domain(domain):
                        domains.add(domain)

        # Поиск в атрибутах src тегов <img>, <script>, <link>
        for tag in soup.find_all(["img", "script", "link"]):
            src = tag.get("src")
            if src:
                parsed_url = urlparse(src)
                if parsed_url.netloc:
                    domain = parsed_url.netloc
                    if target == get_base_domain(domain):
                        domains.add(domain)
        
        # Поиск в других атрибутах, где могут быть URL (например, data-src)
        for tag in soup.find_all(attrs={"data-src": True}):
            src = tag.get("data-src")
            if src:
                parsed_url = urlparse(src)
                if parsed_url.netloc:
                    domain = parsed_url.netloc
                    if target == get_base_domain(domain):
                        domains.add(domain)

        # Фильтрация поддоменов, если нужно
        if not include_subdomains:
            main_domains = set()
            for domain in domains:
                parts = domain.split(".")
                if len(parts) >= 2:
                    main_domain = ".".join(parts[-2:])  # Получаем основной домен (например, example.com)
                    main_domains.add(main_domain)
            return main_domains

        return domains

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе URL: {e}")
        return None
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")
        return None

def check_links(target):
    domains = extract_domains_from_website("https://" + target, target)
    if domains:
        print(f"Найденные домены (с поддоменами): {domains}")
    else:
        print("Не удалось получить домены.")
    print("-" * 20)

# Функция для получения IP по домену
def get_ip_from_domain(domain):
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except Exception as e:
        return f"Error resolving domain: {e}"

# Функция для отправки HTTP-запросов
def send_request(url):
    try:
        response = requests.get(url, timeout=10)
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"