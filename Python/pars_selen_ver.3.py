import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.options import Options


option = Options()
option.set_preference('dom.webdriver.enabled', False)
option.set_preference('dom.webnotifications.enabled', False)
option.set_preference('media.volume_scale', '0.0')
option.add_argument('-headless')  #Комментить, если надо посмотреть, что происходит в браузере.
browser = webdriver.Firefox(options=option)

browser.get("https://dreamjob.ru/vakansii")
    #xpath = "/html/body/main/div/form/div[1]/div[2]/div[1]/div/div[1]"
    #browser.find_element(By.XPATH, xpath).click()

def search_city_and_proff(city, proff): # В функцию передаём город (Будет выбран первый найденный и профессию, по которой искать)
    xpath = "/html/body/main/div/form/div[1]/div[2]/div[1]/div/div[1]"
    browser.find_element(By.XPATH, xpath).click()

    inp_xpath = (
                "/html/body/main/div/form/div[1]/div[2]/div[1] \
                /div/div[2]/div[2]/div[1]/div/input"
                )
    browser.find_element(By.XPATH, inp_xpath).send_keys(city) # Передаём город в блок выбора города (Если что, то сначала его открываем). Комменти опции и увидишь.
    time.sleep(1)
    xpath_from_select_city = (
                            "/html/body/main/div[1]/form/div[1]/div[2]/div[1]/div/div[2]/div[2]/div[2]/div[2]/div/div[1]/span"
                            )
    button_select_city = browser.find_element(By.XPATH, xpath_from_select_city)
    button_select_city.click()

    button_for_input_proff = "/html/body/main/div[1]/form/div[1]/div[1]/div/div/span/input[2]" #Передаём профессию в блок выбора профессии
    browser.find_element(By.XPATH, button_for_input_proff).send_keys(proff)

    button_for_search = "/html/body/main/div/form/div[1]/div[1]/button"
    browser.find_element(By.XPATH, button_for_search).click()

search_city_and_proff('Ека', 'Информационная безопасность')

time.sleep(5) #Таймеры подгонять под железо!!!

page = browser.page_source
browser.close()
soup = BeautifulSoup(page, 'lxml')

href_page = soup.find(class_='pagination').find_all('a', href=True)
list_href = set()
for i in range(len(href_page)):
    list_href.add('https://dreamjob.ru/' + href_page[i].get('href')) # Варим ссылки на страницы (5 страниц, дальше вакансии подбираются менее подходящие.)
                                                                    # Можно распарсить ещё, в зависимости от запроса, но выборка будет крайне размазанная.

list_href = sorted(list_href)

list_vacansy_href = set()
for i in list_href:            # Тут варим суп из страниц, которые получили ранее
    response = requests.get(i).text
    block = BeautifulSoup(response, 'lxml')
    tmp = block.find('div', class_='vacancies-new__list').find_all('a', href=True)
    tmp_set = {'https://dreamjob.ru' + k.get('href') for k in tmp if 'empl' in k.get('href')}
    list_vacansy_href.update(tmp_set)
    time.sleep(5) #Запросы слать с перерывом, иначе заблочит.

print(*sorted(list_vacansy_href), sep='\n')
