
from utils.base_utils import log
import re


def find_subdomains(results, root_domain):
    log(f"Searching subdomains for {root_domain}")
    subdomains = []

    # Обрабатываем results как одну строку
    if isinstance(results, str):
        # Используем findall для поиска *всех* совпадений в строке
        matches = re.findall(r"([\w\.-]+\." + re.escape(root_domain) + r")(?:\.|\s|$)", results, re.IGNORECASE) #улучшенное регулярное выражение
        subdomains.extend(matches)
    elif isinstance(results, list): #для обработки случая если results все таки список строк
        for record in results:
            matches = re.findall(r"([\w\.-]+\." + re.escape(root_domain) + r")(?:\.|\s|$)", record, re.IGNORECASE)
            subdomains.extend(matches)
    else:
        log("results must be str or list")
        return subdomains
    
    return list(set(subdomains)) 


def add_subdomains(session, subdomains, original_ip):
    from models import IPResource, update_ip_domain_association
    from passive.dns import dns_lookup
    if subdomains:
                    log(f"Found subdomain: {subdomains}", "INFO")
                    for subdomain in subdomains:
                        try:
                            subdomain_ip_pool = dns_lookup(subdomain, "A")
                            if subdomain_ip_pool:
                                subdomain_ip = subdomain_ip_pool[0]
                                try:
                                    existing_ip_resource = session.query(IPResource).filter_by(ip_address=subdomain_ip).first()
                                    if existing_ip_resource:
                                        if original_ip and subdomain_ip == original_ip:
                                            log(f"Subdomain {subdomain} has the same IP ({subdomain_ip}) - adding domain to association", "INFO")
                                            existing_ip_resource.add_domain(session, subdomain)
                                        else:
                                            log(f"Subdomain {subdomain} has different IP: {subdomain_ip}", "INFO")
                                            log(f"Updating db ...", "INFO")
                                            update_ip_domain_association(session, subdomain_ip, subdomain)
                                    else:
                                            log(f"IP resource not found for {subdomain_ip}. Creating new resource", "INFO")
                                            update_ip_domain_association(session, subdomain_ip, subdomain)
                                except ValueError:
                                    log(f"Invalid IP address found for subdomain {subdomain}: {subdomain_ip}", "INFO")
                        except Exception as e:
                            log(f"Error getting A record for subdomain {subdomain}: {e}", "INFO")