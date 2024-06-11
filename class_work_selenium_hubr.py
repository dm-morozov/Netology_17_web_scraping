from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

# Работаем с Selenium

def wait_element(browser, delay_second=10, by=By.CLASS_NAME, value=None):
    return WebDriverWait(browser, delay_second).until(
        expected_conditions.presence_of_element_located((by, value))
        )

chrome_path = ChromeDriverManager().install()
browser_service = Service(executable_path=chrome_path)
browser = Chrome(service=browser_service)
browser.get('https://habr.com/ru/articles/')

article_tags_list = browser.find_element(By.CLASS_NAME, 'tm-articles-list')
article_tags = article_tags_list.find_elements(By.TAG_NAME, 'article')
parsed_data = []
for article in article_tags:
    h2_tag = wait_element(article, by=By.TAG_NAME, value='h2')
    time_tag = wait_element(article, by=By.TAG_NAME, value='time')
    a_tag = wait_element(h2_tag, by=By.TAG_NAME, value='a')

    title = a_tag.text
    pub_time = time_tag.get_attribute('datetime')
    link = a_tag.get_attribute('href')

    parsed_data.append(
        {
            'title' : title,
            'pub_time' : pub_time,
            'link': link,
            'text': ''
        }
    )

for parsed_article in parsed_data:
    browser.get(parsed_article['link'])

    article_tag = wait_element(browser, by=By.ID, value='post-content-body')
    article_text = article_tag.text
    parsed_article['text'] = article_text[:100]

print(parsed_data)