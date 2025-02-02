from googlesearch import search
import re

def search_social_media(query):
    try:
        print(f"Поиск по соцсетям и Telegram с запросом: {query}")

        # Используем дорки для направленных поисков
        search_query = f'site:vk.com OR site:ok.ru OR site:t.me {query}'

        results = []
        for result_url in search(search_query, num_results=50, lang="ru"):
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
        if 'vk.com' in url:
            user_info = re.search(r'vk\.com\/([^/]+)', url)
            if user_info:
                processed_info.append(f"ВКонтакте группа: {user_info.group(1)}, URL: {url}")
        elif 'ok.ru' in url:
            processed_info.append(f"Одноклассники группа, URL: {url}")
        elif 't.me' in url:
            telegram_info = re.search(r't\.me\/([^/]+)', url)
            if telegram_info:
                processed_info.append(f"Telegram канал/чат: {telegram_info.group(1)}, URL: {url}")
        else:
            processed_info.append(f"Неизвестный профайл, URL: {url}")
    return processed_info

if __name__ == "__main__":
    query = "МИФИ"
    search_social_media(query)