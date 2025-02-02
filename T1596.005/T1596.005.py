import requests
from bs4 import BeautifulSoup
import sys

def search_scan_data(ip):
    try:
        url = f"https://www.shodan.io/host/{ip}"
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Получение заголовков
            headers = soup.find_all('h1')
            for header in headers:
                print(header.text.strip())
            
            # Получение информации о портах
            ports = soup.find_all('div', class_='port')
            for port in ports:
                port_number = port.find('span', class_='value').text
                service_name = port.find('span', class_='service-name').text
                print(f"Port: {port_number}, Service: {service_name}")

        else:
            print(f"Error fetching data from Shodan: {response.status_code}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scan_search.py <ip>")
    else:
        ip_to_search = sys.argv[1]
        search_scan_data(ip_to_search)