from utils.base_utils import log
from models import IPResource, Email
import requests
from bs4 import BeautifulSoup
import re, socket, time
from utils.subdomains import find_subdomains, add_subdomains

def find_emails(session, soup, domain: str):

    found_emails = set()

    for a_tag in soup.find_all("a", href=re.compile(r"mailto:")):
        email = a_tag["href"][7:]
        if email.endswith("@" + domain):
            found_emails.add(email)

    text = soup.get_text()
    email_pattern = r"[a-zA-Z0-9._%+-]+@" + re.escape(domain)
    for email in re.findall(email_pattern, text):
        found_emails.add(email)

        # Сохранение в базу данных
    saved_emails = []
    for email in found_emails:
        if Email.create(session, email): # Проверяем, что email успешно создан/получен
            saved_emails.append(email)
    return list(saved_emails) # Возвращаем список строк


def check_web_page_for_subdomains(session, target, domain):
    try:
        response = requests.get("https://" + domain, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        emails = find_emails(session, soup, target.domains[0].name)
        log(f"Found emails: {emails}")
        # Извлекаем домены из разных мест HTML
        domains_from_links = [link.get("href") for link in soup.find_all("a") if link.get("href") and target.domains[0].name in link.get("href").lower()] #Ссылки
        domains_from_scripts = [script.get("src") for script in soup.find_all("script") if script.get("src") and target.domains[0].name in script.get("src").lower()] #Скрипты
        domains_from_iframes = [iframe.get("src") for iframe in soup.find_all("iframe") if iframe.get("src") and target.domains[0].name in iframe.get("src").lower()] #Iframe
        domains_from_meta = [meta.get("content") for meta in soup.find_all("meta") if meta.get("content") and target.domains[0].name in meta.get("content").lower()] #Meta теги

        all_domains = domains_from_links + domains_from_scripts + domains_from_iframes + domains_from_meta

        # Фильтрация и очистка доменов
        cleaned_domains = []
        for domain in all_domains:
            if domain.startswith("//"):
                domain = "https:" + domain
            try:
                domain_parts = domain.split("/")
                domain = domain_parts[2] if domain_parts[0].startswith("http") else domain_parts[0]
                if domain.startswith("www."):
                    domain = domain[4:]
                cleaned_domains.append(domain)
            except IndexError:
                pass


        found_subdomains = find_subdomains(cleaned_domains, target.domains[0].name)
        if found_subdomains:
            log(f"Found subdomains on {target.domains[0].name}: {found_subdomains}")
            add_subdomains(session, found_subdomains, target.ip_address)
            return found_subdomains
        else:
            log(f"No subdomains found on {target.domains[0].name}")
            return None

    except requests.exceptions.RequestException as e:
        log(f"Error accessing {target.domains[0].name}: {e}")
        return None
    except Exception as e:
        log(f"An unexpected error occurred: {e}")
        return None


def check_web(session, target):
    web_sub_list = check_web_page_for_subdomains(session, target, target.domains[0].name)
    if not web_sub_list:
        log(f"No subdomains found for {target.domains[0].name}")
        return

    log(f"Found {len(web_sub_list)} subdomains. Starting recon on subdomains.")

    checked_ips = set() # Отслеживаем уже проверенные IP
    max_checks = 10
    delay = 3
    
    for i, full_subdomain in enumerate(web_sub_list):
        log(f"Starting recon on subdomain: {full_subdomain}")

        try:
            # Получаем IP адрес поддомена
            ip_address = socket.gethostbyname(full_subdomain) # Используем socket для DNS lookup
            if ip_address in checked_ips:
                log(f"IP address {ip_address} already checked. Skipping.")
                continue

            # Ищем IPResource в базе данных по IP адресу
            target_resource = session.query(IPResource).filter_by(ip_address=ip_address).first()

            if target_resource:
                log(f"Found target resource for {full_subdomain}: {target_resource}")
                check_web_page_for_subdomains(session, target, full_subdomain) # Вызов check_web_for_subdomains для поддомена
            else:
                log(f"No IPResource found in database for IP address: {ip_address} of subdomain: {full_subdomain}")

            checked_ips.add(ip_address)
            time.sleep(delay)

        except socket.gaierror as e:
            log(f"DNS lookup failed for {full_subdomain}: {e}")
            continue
        except Exception as e:
            log(f"Error during recon on subdomain {full_subdomain}: {e}")