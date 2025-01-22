import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.options import Options
import random

from aiogram import Bot, Dispatcher, F
import asyncio
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


option = Options()
option.set_preference('dom.webdriver.enabled', False)
option.set_preference('dom.webnotifications.enabled', False)
option.set_preference('media.volume_scale', '0.0')
#option.add_argument('-headless')  #Комментить, если надо посмотреть, что происходит в браузере.

    #xpath = "/html/body/main/div/form/div[1]/div[2]/div[1]/div/div[1]"
    #browser.find_element(By.XPATH, xpath).click()

#Функция для поиска ЛЮБЫХ вакансий в ЛЮБОМ городе.
def search_city_and_proff(city, proff):
    browser = webdriver.Firefox(options=option)
    browser.get("https://dreamjob.ru/vakansii")
    xpath = "/html/body/main/div/form/div[1]/div[2]/div[1]/div/div[1]"
    browser.find_element(By.XPATH, xpath).click()

    inp_xpath = (
                "/html/body/main/div/form/div[1]/div[2]/div[1] \
                /div/div[2]/div[2]/div[1]/div/input"
                )
    browser.find_element(By.XPATH, inp_xpath).send_keys(city)
    time.sleep(2)
    xpath_from_select_city = (
                            "/html/body/main/div[1]/form/div[1]/div[2]/div[1]/div/div[2]/div[2]/div[2]/div[2]/div/div[1]/span"
                            )
    button_select_city = browser.find_element(By.XPATH, xpath_from_select_city)
    button_select_city.click()

    button_for_input_proff = "/html/body/main/div[1]/form/div[1]/div[1]/div/div/span/input[2]"
    browser.find_element(By.XPATH, button_for_input_proff).send_keys(proff)

    button_for_search = "/html/body/main/div/form/div[1]/div[1]/button"
    browser.find_element(By.XPATH, button_for_search).click()

    time.sleep(10)
    page = browser.page_source
    browser.close()
    return page

#Из полученного селениумом кода выдираем страницы с вакансиями и вакансии с этих страниц
def get_vacansy_href(page):
    soup = BeautifulSoup(page, 'lxml')

    href_page = soup.find(class_='pagination').find_all('a', href=True)
    total_vacansy_sum = soup.find(class_="vacancies-new__result").text
    list_href = set()
    for i in range(len(href_page)):
        list_href.add('https://dreamjob.ru/' + href_page[i].get('href'))

    list_href = sorted(list_href)

    list_vacansy_href = set()
    for i in list_href:
        response = requests.get(i).text
        block = BeautifulSoup(response, 'lxml')
        tmp = block.find('div', class_='vacancies-new__list').find_all('a', href=True)
        tmp_set = {'https://dreamjob.ru' + k.get('href') for k in tmp if 'empl' in k.get('href')}
        list_vacansy_href.update(tmp_set)
        time.sleep(5)

    #count_user_step = 10 # !!! Число вакансий от юзера, до 50 штук
    list_vacansy_href = list(list_vacansy_href)
    #print(*sorted(list_vacansy_href), sep='\n')
    #print(f'Найдено вакансий: {total_vacansy_sum.strip()}')
    return list_vacansy_href, total_vacansy_sum

#Даём количество вакансий на переваривание и лист с вакансиями, получаем зарплату, название и требования.
def character_vacansy(count_user_step, list_vacansy_href):
    href_dict = dict.fromkeys(list_vacansy_href[:count_user_step], {})
    for i in list_vacansy_href[:count_user_step]:
        tmp_dict = {}
        tmp_url = requests.get(i).text
        vacansy_responce = BeautifulSoup(tmp_url, 'lxml')
        tmp = vacansy_responce.find(class_='job-vacancy__block block-24-16 job-vacancy__description').text

        tmp_job_vacansy_salary = vacansy_responce.find(class_='job-vacancy__salary').text
        tmp_dict['salary'] = (tmp_job_vacansy_salary if len(tmp_job_vacansy_salary) > 3 else 'Не указана')

        name_vacansy = vacansy_responce.find(class_='job-vacancy__head').text
        tmp_dict['name'] = name_vacansy

        if 'Требования' in tmp:
            tmp = tmp[tmp.find('Требования'):]
            tmp = tmp[:tmp.find('\n')]
            tmp_dict['skills'] = tmp
        elif 'Что мы ждём от кандидата' in tmp:
            tmp = tmp[tmp.find('Что мы ждём от кандидата'):]
            tmp = tmp[:tmp.find('\n')]
            tmp_dict['skills'] = tmp
        elif 'Что мы ждем от кандидата' in tmp:
            tmp = tmp[tmp.find('Что мы ждем от кандидата'):]
            tmp = tmp[:tmp.find('\n')]
            tmp_dict['skills'] = tmp
        elif 'Наши ожидания от кандидата' in tmp:
            tmp = tmp[tmp.find('Наши ожидания от кандидата'):]
            tmp = tmp[:tmp.find('\n')]
            tmp_dict['skills'] = tmp
        elif 'Задачи' in tmp:
            tmp = tmp[tmp.find('Задачи'):]
            tmp = tmp[:tmp.find('\n')]
            tmp_dict['skills'] = tmp
        elif 'Обязанности' in tmp:
            tmp = tmp[tmp.find('Обязанности'):]
            tmp = tmp[:tmp.find('\n')]
            tmp_dict['skills'] = tmp
        else:
            tmp_dict['skills'] = 'Требования не указаны...'
        href_dict[i] = tmp_dict
        time.sleep(random.randrange(3, 10))
    salary_stat = ''
    for i in href_dict:
        salary_stat += href_dict[i]['salary'].strip() + '@'
    return href_dict, salary_stat



#####################################
#Телеграм бот, библиотека aiogram
bot = Bot(token='')
dp = Dispatcher()

kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Я хочу найти вакансии')],
    [KeyboardButton(text='Я хочу узнать статистику')]
], resize_keyboard=True, input_field_placeholder='Тебе кнопки зачем?'
)


class info_vacansy(StatesGroup):
    city = State()
    vacansy = State()
    step_vacansy = State()


async def main():
    await dp.start_polling(bot)


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Привет. Нажми кнопку.\nВнимание, ожидание ~ 2 минуты', reply_markup=kb)


@dp.message(F.text == 'Я хочу найти вакансии')
async def vacansy_cnt(message: Message, state: FSMContext):
    await state.set_state(info_vacansy.city)
    await message.answer('Введи город')

@dp.message(info_vacansy.city)
async def city_save(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(info_vacansy.vacansy)
    await message.answer('Введи название профессии')


@dp.message(info_vacansy.vacansy)
async def vacansy_save(message: Message, state: FSMContext):
    await state.update_data(vacansy=message.text)
    await state.set_state(info_vacansy.step_vacansy)
    await message.answer('Введи количество вакансий (До 50)')


@dp.message(info_vacansy.step_vacansy)
async def step_save(message: Message, state: FSMContext):
    await state.update_data(step_vacansy=message.text)
    info_send = await state.get_data()
    for i in info_send:    
        await message.answer(f'{i}:{info_send[i]}')
    page_sourse = search_city_and_proff(info_send['city'], info_send['vacansy'])
    last_list, no_more = get_vacansy_href(page_sourse)
#    for i in last_list:
#        await message.answer(i)
#        time.sleep(2)
#    await message.answer(last_list)
    last_dict, salary_info = character_vacansy(int(info_send['step_vacansy']), last_list)
#    await message.answer(last_dict)
    for i, j in last_dict.items():
        await message.answer(f'Ссылка на вакансию: {i}\nВакансия: {j['name']}\nЗаработная плата: {j['salary']}\nТребования:\n{j['skills']}')
        time.sleep(2)
    await state.clear()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')    
