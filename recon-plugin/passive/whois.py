from utils.base_utils import log
import whois, json
from utils.net_utils import parse_whois_info
from utils.subdomains import find_subdomains, add_subdomains

# Техника T1596.002(Whois Data)
def whois_lookup(target):
    domain = target.domains[0].name
    try:
        domain_info = whois.whois(domain)
        parsed_info = parse_whois_info(domain_info)
        if parsed_info:
            log(f"Whois information for {domain}: {parsed_info}", "INFO")
            target.whois_data = json.dumps(parsed_info, default=str)
        else:
            log(f"Error requesting whois for {domain}", "ERROR")
        return parsed_info

    except Exception as e:
        log(f"Error performing whois lookup for {domain}: {e}", "ERROR")
        return None

def check_whois_for_subdomains(session, target):
    log(f"Checking subdomains in whois for {target.domains[0].name}", "INFO")
    subdomains = find_subdomains(target.whois_data, target.domains[0].name)
    if subdomains:
        add_subdomains(session, subdomains, target.ip_address)
    else:
        log(f"No subdomains in whois for {target.domains[0].name}", "INFO")