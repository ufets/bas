from utils.base_utils import log
from passive.dns import get_dns_records
from passive.whois import whois_lookup, check_whois_for_subdomains

def passive_recon(session, target):
    log(f"Starting passive reconnaissance on {target}")
    whois_lookup(target)
    check_whois_for_subdomains(session, target)
    get_dns_records(session, target)