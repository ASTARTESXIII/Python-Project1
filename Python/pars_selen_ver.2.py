import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

browser = webdriver.Firefox()

browser.get("https://dreamjob.ru/vakansii")
    #xpath = "/html/body/main/div/form/div[1]/div[2]/div[1]/div/div[1]"
    #browser.find_element(By.XPATH, xpath).click()

def search_city_and_proff(city, proff):
    xpath = "/html/body/main/div/form/div[1]/div[2]/div[1]/div/div[1]"
    browser.find_element(By.XPATH, xpath).click()

    inp_xpath = (
                "/html/body/main/div/form/div[1]/div[2]/div[1] \
                /div/div[2]/div[2]/div[1]/div/input"
                )
    browser.find_element(By.XPATH, inp_xpath).send_keys(city)
    time.sleep(1)
    xpath_from_select_city = (
                            "/html/body/main/div[1]/form/div[1]/div[2]/div[1]/div/div[2]/div[2]/div[2]/div[2]/div/div[1]/span"
                            )
    button_select_city = browser.find_element(By.XPATH, xpath_from_select_city)
    button_select_city.click()

    button_for_input_proff = "/html/body/main/div[1]/form/div[1]/div[1]/div/div/span/input[2]"
    browser.find_element(By.XPATH, button_for_input_proff).send_keys(proff)

    button_for_search = "/html/body/main/div/form/div[1]/div[1]/button"
    browser.find_element(By.XPATH, button_for_search).click()

search_city_and_proff('Ека', 'Информационная безопасность')

time.sleep(5)

page = browser.page_source
soup = BeautifulSoup(page, 'lxml')

href_page = soup.find(class_='pagination').find_all('a', href=True)
list_href = set()
for i in range(len(href_page)):
    list_href.add('https://dreamjob.ru/' + href_page[i].get('href'))

print(*sorted(list_href), sep='\n')
