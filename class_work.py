import requests
from bs4 import BeautifulSoup
from fake_headers import Headers

def get_headers():
    return Headers(browser="chrome", os="win").generate()

url = 'https://www.iplocation.net/'
response = requests.get(url)

if response.status_code == 200:

    html_content = response.content
    # Создайте объект BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Извлеките заголовок страницы
    title = soup.title.text
    print(f'Title: {title}')

    span_element = soup.find('span', class_ = 'table-ip4-home')

    if span_element:
        ip_address = span_element.text.strip()
        print(f"IP address: {ip_address}")
    else:
        print("Element not found")


# Работаем с Habr

url_habr = "https://habr.com/ru/articles/"
response_habr = requests.get(url_habr, headers=get_headers())
html_content_habr_main = response_habr.content

if response_habr.status_code == 200:
    soup_main = BeautifulSoup(html_content_habr_main, 'lxml')
    articles_list = soup_main.find('div', class_='tm-articles-list')
    articles = articles_list.find_all('article', class_='tm-articles-list__item')
    
    parsed_data = []

    for article in articles:

        time = article.find('time')['datetime']
        tm_title = article.find('h2', class_='tm-title')
        link = 'https://habr.com' + tm_title.find('a')['href']
        title = tm_title.find('span').text
        # print(time, link, title)

        full_discription = requests.get(link, headers=get_headers())
        
        if full_discription.status_code == 200: 
            html_content_habr_full_discription = full_discription.content
            soup_discription = BeautifulSoup(html_content_habr_full_discription, 'lxml')
            discription = soup_discription.find('div', id='post-content-body').text[:100]
            # print(discription)

        parsed_data.append({
            'time' : time, 
            'link': link, 
            'title' : title, 
            'discription' : discription
            })
    
    print(parsed_data)
