import time
from selenium import webdriver
from selenium.webdriver.common.by import By

browser = webdriver.Firefox()
# C:\Users\zebzeev.SUNNY\Desktop\Python\def_parsinh

browser.get("https://dreamjob.ru/vakansii")
xpath = "/html/body/main/div/form/div[1]/div[2]/div[1]/div/div[1]"
browser.find_element(By.XPATH, xpath).click()
inp_xpath = (
    "/html/body/main/div/form/div[1]/div[2]/div[1]/div/div[2]/div[2]/div[1]/div/input"
)
browser.find_element(By.XPATH, inp_xpath).send_keys("Екатеринбург")
xpath_from_city = (
    "/html/body/main/div/form/div[1]/div[2]/div[1]/div/div[2]/div[2]/div[2]"
)
browser.find_element(By.XPATH, xpath_from_city).click()
button_for_search = "/html/body/main/div/form/div[1]/div[1]/button"
time.sleep(3)
browser.find_element(By.XPATH, button_for_search).click()
