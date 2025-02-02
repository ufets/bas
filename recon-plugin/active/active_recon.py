from utils.base_utils import log
from active.web import check_web
from active.scanner.scan import check_open_ports, scan_vulnerabilities

def active_recon(session, target):
    log(f"Starting active reconnaissance on {target}")
    check_web(session, target)
    #check_open_ports(session, target)
    #print("SCAN RES: ", scan_vulnerabilities( '147.45.147.79'))