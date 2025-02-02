import requests

def detect_waf(url):

    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': url,
        'Cookie': 'test=wafdetector'
    }

    test_payloads = [
        "' OR 1=1--",  
        "<script>alert(1)</script>", 
        "<?php phpinfo(); ?>",  
    ]

    try:
        response = requests.get(url, headers=headers, timeout=3)

        # Проверка стандартных заголовков WAF
        waf_headers = ['x-waf', 'x-nginx-status', 'Server', 'X-Powered-By']
        for header in waf_headers:
            if header in response.headers:
                print(f'WAF detected by header: {header}')
                return True

        # Проверка задержки
        if response.elapsed.total_seconds() > 2:
            print('WAF might be delaying requests.')
        
        for payload in test_payloads:
            injected_response = requests.get(f"{url}/?q={payload}", headers=headers, timeout=3)
            if injected_response.status_code in [403, 406, 500]:
                print(f'WAF detected by blocking payload: {payload}')
                return True

        print('No evidence of WAF detected.')
        return False

    except requests.RequestException as e:
        print(f'Request failed: {e}')
        return False

# Пример использования
target_url = 'https://mephi.ru'
detect_waf(target_url)