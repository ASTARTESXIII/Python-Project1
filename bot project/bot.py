import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Функция для сбора вакансий
def fetch_vacancies(region):
    url = f'https://api.hh.ru/vacancies?text=информационная+безопасность&area={region}'
    response = requests.get(url)

    if response.status_code == 200:
        vacancies = response.json()
        # Фильтрация вакансий по ключевым словам
        keywords = ["информационная безопасность", "пентестер", "специалист по информационной безопасности", 
                    "администратор по информационной безопасности", "анализ безопасности", "инженер по безопасности"]
        filtered_vacancies = [
            vacancy for vacancy in vacancies['items']
            if any(keyword in vacancy['name'].lower() for keyword in keywords)
        ]
        return len(filtered_vacancies), filtered_vacancies
    else:
        return 0, []

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет! Введите команду /vacancies, чтобы найти вакансии в Екатеринбурге.')

# Команда /vacancies
async def vacancies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    region = 3  # ID для Екатеринбурга
    count, vacancies = fetch_vacancies(region)

    if count == 0:
        await update.message.reply_text('Вакансии не найдены.')
    else:
        message = "Найденные вакансии на hh.ru:\n\n"
        
        for vacancy in vacancies:
            title = vacancy['name']
            salary = vacancy.get('salary')
            if salary:
                salary_info = f"{'от ' + str(salary['from']) + ' RUR' if salary['from'] else 'Зарплата не указана'}"
            else:
                salary_info = "Зарплата не указана"
            company = vacancy['employer']['name']
            link = vacancy['alternate_url']
            
            message += (
                f"Вакансия: {title}\n"
                f"Зарплата: {salary_info}\n"
                f"Компания: {company}\n"
                f"Ссылка: {link}\n\n"
            )
        
        await update.message.reply_text(message)

# Основная функция
if __name__ == '__main__':
    app = ApplicationBuilder().token('7891800291:AAHaImzymyPDMTNzXhqHOg_MK6Cs_9_MY68').build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('vacancies', vacancies))

    app.run_polling()