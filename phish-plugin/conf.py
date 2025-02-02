import json
import logger
def load_conf(path):
    try:
        with open(path, "r", encoding='utf-8') as config_file:
            config = json.load(config_file)
            return config  # Возвращаем словарь
    except FileNotFoundError:
        logger.error(f"Error: Config file not found at {path}")
        return None  # Или выбросить исключение, если это необходимо
    except json.JSONDecodeError:
        logger.error(f"Error: Invalid JSON format in {path}")
        return None

