import requests
import re
import sys
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

def extract_subdomains(html, domain_filter, found_subdomains):
    """Извлекает поддомены, фильтрует их по домену и убирает дубликаты."""
    # Используем регулярное выражение для поиска всех поддоменов в доменах
    subdomains = set(re.findall(r"https?://([a-zA-Z0-9.-]+)", html))
    new_subdomains = {subdomain for subdomain in subdomains if domain_filter in subdomain and subdomain not in found_subdomains}
    return new_subdomains

def get_links(url, html, base_domain, visited):
    """Находит внутренние ссылки, избегая зацикливания."""
    soup = BeautifulSoup(html, "html.parser")
    links = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        full_url = urljoin(url, href)
        parsed_url = urlparse(full_url)

        if parsed_url.netloc and base_domain in parsed_url.netloc and full_url not in visited:
            links.add(full_url)
    
    return links

def crawl(url, domain_filter, max_depth, visited=None, found_subdomains=None, depth=1):
    """Рекурсивный обход страниц с поиском поддоменов и защитой от зацикливания."""
    if visited is None:
        visited = set()
    if found_subdomains is None:
        found_subdomains = set()

    if url in visited or depth > max_depth:
        return

    print(f"[+] Обход: {url} (Глубина {depth})")
    visited.add(url)

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        print(f"[-] Ошибка при доступе к {url}")
        return

    new_subdomains = extract_subdomains(response.text, domain_filter, found_subdomains)
    
    if new_subdomains:
        found_subdomains.update(new_subdomains)
        print(f"[!] Найдены поддомены на {url}: {', '.join(new_subdomains)}")
        with open("subdomains.txt", "a", encoding="utf-8") as f:
            for subdomain in sorted(new_subdomains):
                f.write(subdomain + "\n")

    links = get_links(url, response.text, urlparse(url).netloc, visited)

    time.sleep(2)  # Задержка между запросами

    for link in links:
        crawl(link, domain_filter, max_depth, visited, found_subdomains, depth + 1)

def main():
    if len(sys.argv) != 4:
        print("Использование: python script.py <URL> <домен> <глубина>")
        print("Пример: python script.py https://mephi.ru mephi.ru 5")
        sys.exit(1)

    start_url = sys.argv[1]
    domain_filter = sys.argv[2]
    
    try:
        max_depth = int(sys.argv[3])
    except ValueError:
        print("Ошибка: глубина должна быть числом!")
        sys.exit(1)

    print(f"[*] Запуск обхода {start_url} с глубиной {max_depth} и фильтром {domain_filter}")

    open("subdomains.txt", "w").close()  # Очистка файла перед началом

    crawl(start_url, domain_filter, max_depth)

    print(f"\n[✔] Готово! Уникальные поддомены сохранены в subdomains.txt")

if __name__ == "__main__":
    main()
