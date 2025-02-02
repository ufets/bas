import requests
import sys

def get_client_config(ip):
    try:
        response = requests.get(f'http://{ip}', timeout=5)
        
        # Сбор заголовков ответа
        print("Заголовки ответа:")
        for header, value in response.headers.items():
            print(f"{header}: {value}")
        
        # Извлечение информации 'Server' и 'X-Powered-By'
        server_info = response.headers.get('Server')
        x_powered_by = response.headers.get('X-Powered-By')
        print('Информация о сервере:', server_info)
        print('X-Powered-By:', x_powered_by)
        
        # Проверка на технологии и уязвимости
        check_for_technologies_and_vulnerabilities(response.text)

    except requests.RequestException as e:
        print(f'Ошибка при запросе к {ip}: {e}')

def check_for_technologies_and_vulnerabilities(html_content):
    # Простой пример поиска признаков популярных технологий
    if 'wp-content' in html_content:
        print('WordPress выявлен на сайте.')
    
    if 'csrf-token' in html_content:
        print('На сайте защита CSRF.')

    # Использование регулярных выражений для поиска конкретных технологий
    if 'jquery' in html_content:
        print('Используется jQuery.')
    
    # Поиск стандартных фрагментов круга популярных фреймворков
    if 'vue.js' in html_content:
        print('Используется Vue.js.')
    if 'react' in html_content and 'component' in html_content:
        print('Используется React.')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python T1592.004.py <ip_address>")
    else:
        get_client_config(sys.argv[1])