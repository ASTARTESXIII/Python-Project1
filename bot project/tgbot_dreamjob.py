import requests
from bs4 import BeautifulSoup
import telebot

bot = telebot.TeleBot('8033191047:AAHWMjVwGp0kxt99mqSGW8-cqhB1m1rnQic')
city_number = (
    {}
)  # Я словари ещё не прошёл блин, не могу ассоциации по номерам простроить, скоро уже пройду.

url = f"https://dreamjob.ru/vakansii?jbfrp[text]=%D0%B8%D0%BD%D1%84%D0%BE%D1%80%D0%BC%D0%B0%D1%86%D0%B8%D0%BE%D0%BD%D0%BD%D0%B0%D1%8F%20%D0%B1%D0%B5%D0%B7%D0%BE%D0%BF%D0%B0%D1%81%D0%BD%D0%BE%D1%81%D1%82%D1%8C"
response = requests.get(url).text
soup = BeautifulSoup(response, "lxml")
block = soup.find("div", class_="vacancies-new__list")

def cycle_returns(block, message):
    vacancy_list = block.find_all("h4", class_="vacancy-new__heading")
    href = block.find_all(class_="vacancy-new__main-link", href=True)
    previous = block.find_all("p", class_="vacancy-new__text-preview")
    msg = ''
    for i in range(len(href)):
        msg += f'{vacancy_list[i].text}\n' + f'{previous[i].text}\n' + f'{"https://dreamjob.ru" + href[i].get("href")}\n' + '\n'
    bot.send_message(message.from_user.id, msg)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Дай знать":
        cycle_returns(block, message)
    else:
        bot.send_message(message.from_user.id, "Гуляй")
bot.polling(none_stop=True, interval=0)
