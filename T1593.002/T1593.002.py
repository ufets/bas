from googlesearch import search
import re
import time
def search_and_process_info(query):
    try:
        print(f"Поиск по запросу: {query}")

        results = []
        for result_url in search(query, num_results=10, lang="ru"):
            results.append(result_url)
        
        structured_results = process_results(results)
        
        for item in structured_results:
            print(item)

    except Exception as e:
        print(f"Ошибка поиска: {e}")

def process_results(result_urls):
    processed_info = []
    for url in result_urls:
        # Обработка url для выделения ключевых сведений
        domain = re.search(r'://([^/]+)/', url)
        if domain:
            domain_name = domain.group(1)
            processed_info.append(f"Домен: {domain_name}, URL: {url}")
        else:
            processed_info.append(f"Неизвестный домен, URL: {url}")
    return processed_info

if __name__ == "__main__":
    queries = ["МИФИ site:ru filetype:pdf",
               "МИФИ site:ru filetype:docx",
               "ИИКС site:ru filetype:pdf",
               "ИИКС site:ru filetype:docx"
               "mephi site:ru filetype:pdf",
               "mephi site:ru filetype:docx",
               "mephi site:ru filetype:conf",
               "mephi site:ru filetype:txt",
               "mephi site:ru filetype:txt",]
    for query in queries:
        search_and_process_info(query)
        time.sleep(1)