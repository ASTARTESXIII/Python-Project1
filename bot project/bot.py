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
def fetch_vacancies():
    url = 'https://api.hh.ru/vacancies'
    keywords = {
        "информационная безопасность", "пентестер", "специалист по информационной безопасности",
        "администратор по информационной безопасности", "анализ безопасности", "инженер по безопасности",
        "сервисы информационной безопасности", "информационной безопасности",
        "специалист по информационной безопасности (IT компания)", "ведущий инженер по информационной безопасности",
        "специалист по защите информации", "аналитик по информационной безопасности",
        "инженер по защите информации", "менеджер по защите ИТ-инфраструктуры",
        "отдел информационной безопасности региона", "системный инженер по SIEM",
        "ведущий специалист по защите информации", "инженер-аналитик информационной безопасности"
    }
    all_vacancies = []
    page = 0

    while True:
        params = {
            'text': 'информационная безопасность',
            'area': 113,  # Россия
            'page': page,
            'per_page': 50  # Максимально возможное значение
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            break

        vacancies = response.json()
        items = vacancies.get('items', [])
        if not items:
            break

        filtered_vacancies = [
            vacancy for vacancy in items
            if any(keyword in vacancy['name'].lower() for keyword in keywords)
        ]
        all_vacancies.extend(filtered_vacancies)

        page += 1
        if page >= vacancies.get('pages', 1):  # Проверяем, достигли ли последней страницы
            break

    return len(all_vacancies), all_vacancies

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет! Введите команду /vacancies, чтобы найти вакансии по всей России.')

# Команда /vacancies
async def vacancies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверяем, указал ли пользователь количество вакансий
    try:
        limit = int(context.args[0]) if context.args else 20  # По умолчанию 20
        if limit > 100:
            limit = 100  # Ограничим максимум до 100, чтобы не перегружать бот
    except ValueError:
        await update.message.reply_text("Пожалуйста, укажите корректное число после команды /vacancies.")
        return

    count, vacancies = fetch_vacancies()

    if count == 0:
        await update.message.reply_text('Вакансии не найдены.')
    else:
        message = "Найденные вакансии на hh.ru по всей России:\n\n"
        batch_size = 10  # Количество вакансий в одном сообщении
        vacancies = vacancies[:limit]  # Обрезаем до указанного лимита

        for i, vacancy in enumerate(vacancies, 1):
            title = vacancy['name']
            salary = vacancy.get('salary')
            if salary:
                salary_info = []
                if salary.get('from'):
                    salary_info.append(f"от {salary['from']} RUR")
                if salary.get('to'):
                    salary_info.append(f"до {salary['to']} RUR")
                salary_info = " ".join(salary_info) if salary_info else "Зарплата не указана"
            else:
                salary_info = "Зарплата не указана"
            company = vacancy['employer']['name']
            link = vacancy['alternate_url']
            
            message += (
                f"📌 *Вакансия*: {title}\n"
                f"💰 *Зарплата*: {salary_info}\n"
                f"🏢 *Компания*: {company}\n"
                f"🔗 [Ссылка на вакансию]({link})\n"
                "---\n"
            )
            
            # Отправляем сообщение каждые batch_size вакансий
            if i % batch_size == 0 or i == len(vacancies):
                await update.message.reply_text(message, parse_mode='Markdown')
                message = ""  # Очищаем сообщение для следующей партии

# Основная функция
if __name__ == '__main__':
    app = ApplicationBuilder().token('7891800291:AAHaImzymyPDMTNzXhqHOg_MK6Cs_9_MY68').build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('vacancies', vacancies))

    app.run_polling()