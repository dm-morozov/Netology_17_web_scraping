import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import json
from pprint import pprint


# Функция для ожидания элемента
def wait_element(browser, delay_second=1, by=By.CLASS_NAME, value=None):
    return WebDriverWait(browser, delay_second).until(
        EC.presence_of_element_located((by, value))
    )

# Настройка Selenium и запуск браузера
chrome_path = ChromeDriverManager().install()
browser_service = Service(executable_path=chrome_path)
browser = Chrome(service=browser_service)

# Открытие страницы с вакансиями (К Москве и Санкт-Петербургу добавил еще и Оренбург)
url = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2&area=70'
browser.get(url)


# Ожидание загрузки списка вакансий
vacancy_page = wait_element(browser, by=By.CLASS_NAME, value='HH-MainContent')

# Извлечение HTML содержимого элемента
vacancy_html = vacancy_page.get_attribute('outerHTML')

# print(vacancy_html)

soup = BeautifulSoup(vacancy_html, 'lxml')
vacansies = soup.find_all('div', class_='serp-item_link')

# print(vacansies)

# Сбор данных о вакансиях
parsed_date = []
keywords = ['Django', 'Flask']
pattern = r'\d+ ?\d+\s'
pattern_compile = re.compile(pattern)

# Записать в json информацию о каждой вакансии - 
# ссылка, вилка зп, название компании, город
item = 0

for vacancy in vacansies[:50]:

    salary_text = vacancy.find('span', class_='bloko-text').text if vacancy.find('span', class_='bloko-text') else 'Цена не указана' 
    salary_fork = [int(num.replace('\u202f', '')) for num in re.findall(r'\d+\u202f\d+', salary_text)]
    
    # Ищем валюту и сохраняем ее строкой, а не списком (findall)
    currency_ = re.search(r'\$', salary_text)
    currency = currency_.group(0) if currency_ else None

    # Нам не за чем даже заходить на страницы, где валюта не доллар
    if not currency:
        continue

    header_html = vacancy.find('h2', class_='bloko-header-section-2')
    header = header_html.text
    link = header_html.find('a', class_='bloko-link')['href']
    company_name = vacancy.find('a', class_='bloko-link bloko-link_kind-secondary').text
    city = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-address'}).text

    # Переход по ссылке вакансии для извлечения полного описания
    browser.get(link)
    description_page = wait_element(browser, by=By.CLASS_NAME, value='main-content')
    description_html = description_page.get_attribute('innerHTML')

    soup_description = BeautifulSoup(description_html, 'lxml')
    description = soup_description.find('div', {'data-qa': 'vacancy-description'}).text

    if any(keyword in description for keyword in keywords):
        item += 1
        parsed_date.append({
            'link': link, 
            'salary_fork': salary_fork,
            'currency': currency,
            'company_name': company_name, 
            'city': city, 
            'description': description
            })

with open('vacancies.json', 'w', encoding='utf-8') as file:
    json.dump(parsed_date, file, indent=4, ensure_ascii=False)

pprint(parsed_date)
print(f"Количество найденных вакансий: {item}")

browser.quit()
