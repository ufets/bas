
from datetime import datetime

def format_datetime(value):
    if isinstance(value, (datetime, list)):
        if isinstance(value, list):
            return [v.isoformat() if isinstance(v, datetime) else v for v in value]
        return value.isoformat()
    return value

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    colored_timestamp = f"{Colors.CYAN}[{timestamp}]{Colors.RESET}"
    if level == "ERROR":
        colored_level = f"{Colors.RED}{level}{Colors.RESET}"
    elif level == "INFO":
        colored_level = f"{Colors.GREEN}{level}{Colors.RESET}"
    elif level == "WARNING":
        colored_level = f"{Colors.YELLOW}{level}{Colors.RESET}"
    elif level == "DEBUG":
        colored_level = f"{Colors.BLUE}{level}{Colors.RESET}"

    else:
        colored_level = level

    print(f"[{colored_timestamp}] [{colored_level}] {message}")