import logging
import requests
import csv
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

TOKEN = "7555084230:AAHUDNfvjGduPeULzaNSWV3swoDB3Jh6HRc"
MAX_VACANCIES = 100  # Максимум 100 вакансий для запроса
VACANCIES_FILE = "vacancies.csv"
ANALYSIS_FILE = "analysis.csv"
global_nowVac = ""
offset_loadmore = 0
search_data = {}

def write_vacancies_to_csv(vacancies):
    with open(VACANCIES_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['name', 'Компания', 'Зарплата', 'Ссылка', 'Адрес', 'Требования'])
        writer.writeheader()
        writer.writerows(vacancies)

def write_analysis_to_csv(analysis):
    with open(ANALYSIS_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Количество вакансий', 'Средняя зп', 'Мин зп', 'Макс зп', 'Частые требования', 'Рекомендации'])
        writer.writeheader()
        writer.writerows(analysis)

def fetch_vacancies(query, offset=0):
    url = 'https://api.hh.ru/vacancies'
    global offset_loadmore
    offset_loadmore += 11
    all_vacancies = []
    per_page = offset_loadmore
    params = {'text': query, 'area': 113, 'page': offset, 'per_page': per_page}
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        return []
    
    vacancies = response.json().get('items', [])
    for vacancy in vacancies:
        name = vacancy.get('name', 'Без названия')
        employer_name = vacancy.get('employer', {}).get('name', 'Не указана')
        salary = vacancy.get('salary', {})
        salary_info = "не указана"
        if salary:
            from_salary = salary.get('from')
            to_salary = salary.get('to')
            if from_salary and to_salary:
                salary_info = f"от {from_salary} до {to_salary} RUB"
            elif from_salary:
                salary_info = f"от {from_salary} RUB"
            elif to_salary:
                salary_info = f"до {to_salary} RUB"
        address = vacancy.get('address', {}).get('raw', 'Удаленная работа') if vacancy.get('address') else 'Не указан'
        requirements = vacancy.get('snippet', {}).get('requirement', 'Не указаны')
        all_vacancies.append({
            'name': name,
            'Компания': employer_name,
            'Зарплата': salary_info,
            'Ссылка': vacancy.get('alternate_url', 'Не указана'),
            'Адрес': address,
            'Требования': requirements})

    return all_vacancies

def analyze_salaries(vacancies):
    salaries = []
    for vacancy in vacancies:
        salary_str = vacancy['Зарплата']
        
        if 'от' in salary_str and 'до' in salary_str:
            try:
                salary_parts = salary_str.split()
                from_salary = int(salary_parts[1]) if len(salary_parts) > 1 else None
                to_salary = int(salary_parts[3]) if len(salary_parts) > 3 else None
                if from_salary:
                    salaries.append(from_salary)
                if to_salary:
                    salaries.append(to_salary)
            except ValueError:
                continue 
        elif 'от' in salary_str:
            try:
                from_salary = int(salary_str.split()[1])
                salaries.append(from_salary)
            except ValueError:
                continue
        elif 'до' in salary_str:
            try:
                to_salary = int(salary_str.split()[3]) if len(salary_str.split()) > 3 else None
                if to_salary:
                    salaries.append(to_salary)
            except ValueError:
                continue
    
    if salaries:
        avg_salary = sum(salaries) // len(salaries)
        min_salary = min(salaries)
        max_salary = max(salaries)

        return {
            'avg_salary': avg_salary,
            'min_salary': min_salary,
            'max_salary': max_salary,}
    return {
        'avg_salary': 'не указана',
        'min_salary': 'не указана',
        'max_salary': 'не указана',}

def recommend_skills(vacancies):
    all_requirements = ' '.join([vacancy['Требования'] if vacancy['Требования'] else '' for vacancy in vacancies]).lower()
    skill_keywords = ['python', 'sql', 'linux', 'java', 'c++', 'networking', 'security', 'cloud', 'aws', 'data']
    recommended_skills = [skill for skill in skill_keywords if skill in all_requirements]

    if recommended_skills:
        return f"Рекомендуемые навыки: {', '.join(recommended_skills)}"
    return "Нет явных рекомендаций по навыкам."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    global offset_loadmore
    offset_loadmore = 0    
    if os.path.exists(ANALYSIS_FILE):
        os.remove(ANALYSIS_FILE)
    if os.path.exists(VACANCIES_FILE):
        os.remove(VACANCIES_FILE)
    
    context.user_data.clear()
    context.user_data['search_in_progress'] = False
    context.user_data['waiting_for_number'] = False
    await update.message.reply_text(
        "Привет! Напишите вакансию, которую вы хотите подобрать. Например: 'информационная безопасность'.")

async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    global global_nowVac
    global_nowVac = query
    if context.user_data.get('search_in_progress', False):
        await update.message.reply_text("Вы уже находитесь в процессе поиска. Завершите текущий запрос.")
        return

    context.user_data['search_in_progress'] = True
    await update.message.reply_text("В данный момент получаю вакансии, подождите немного...")
    vacancies = fetch_vacancies(query)
    
    if not vacancies:
        await update.message.reply_text("Не удалось найти вакансии по вашему запросу.")
        context.user_data['search_in_progress'] = False
        return

    write_vacancies_to_csv(vacancies)
    salary_analysis = analyze_salaries(vacancies)
    skill_recommendations = recommend_skills(vacancies)
    analysis_data = [{
        'Количество вакансий': len(vacancies),
        'Средняя зп': salary_analysis.get('avg_salary', 'не указана'),
        'Мин зп': salary_analysis.get('min_salary', 'не указана'),
        'Макс зп': salary_analysis.get('max_salary', 'не указана'),
        'Частые требования': ' '.join(skill_recommendations.split()[2:]),
        'Рекомендации': skill_recommendations}]
    
    write_analysis_to_csv(analysis_data)
    for vacancy in vacancies[:11]:
        try:
            await update.message.reply_text(
                f"🔹 {vacancy['name']}\n"
                f"🏢 Компания: {vacancy['Компания']}\n"
                f"💰 Зарплата: {vacancy['Зарплата']}\n"
                f"📍 Адрес: {vacancy['Адрес']}\n"
                f"📑 Требования: {vacancy['Требования']}\n"
                f"🔗 Ссылка: <{vacancy['Ссылка']}>",  # Используем < > для ссылки
                parse_mode="Markdown", disable_web_page_preview=True
            )
        except Exception as e:
            logging.error(f"Ошибка при отправке вакансии: {e}")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists(ANALYSIS_FILE):
        with open(ANALYSIS_FILE, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            analysis_data = list(reader)
            
            if analysis_data:
                analysis = analysis_data[0]
                await update.message.reply_text(
                    f"📊 Анализ вакансий:\n"
                    f"🔹 Количество вакансий: {analysis['Количество вакансий']}\n"
                    f"💰 Средняя зп: {analysis['Средняя зп']}\n"
                    f"📉 Мин зп: {analysis['Мин зп']}\n"
                    f"📈 Макс зп: {analysis['Макс зп']}\n"
                    f"💡 Частые требования: {analysis['Частые требования']}\n"
                    f"🔧 Рекомендации: {analysis['Рекомендации']}")
            else:
                await update.message.reply_text("Нет данных для анализа.")
    else:
        await update.message.reply_text("Файл анализа не найден.")

async def load_more(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global global_nowVac
    query = str(global_nowVac)
    offset = context.user_data.get('offset', 0)
    new_vacancies = fetch_vacancies(query, offset=offset)
    
    if not new_vacancies:
        await update.message.reply_text("Новых вакансий не найдено.")
        return
    try:
        with open(VACANCIES_FILE, mode='r', encoding='utf-8') as file:
            existing_vacancies = list(csv.DictReader(file))
    except FileNotFoundError:
        existing_vacancies = []

    unique_vacancies = [vacancy for vacancy in new_vacancies if vacancy not in existing_vacancies]    
    if unique_vacancies:
        existing_vacancies.extend(unique_vacancies)
        write_vacancies_to_csv(existing_vacancies)
        salary_analysis = analyze_salaries(existing_vacancies)
        skill_recommendations = recommend_skills(existing_vacancies)
        analysis_data = [{
            'Количество вакансий': len(existing_vacancies),
            'Средняя зп': salary_analysis.get('avg_salary', 'не указана'),
            'Мин зп': salary_analysis.get('min_salary', 'не указана'),
            'Макс зп': salary_analysis.get('max_salary', 'не указана'),
            'Частые требования': ' '.join(skill_recommendations.split()[2:]),
            'Рекомендации': skill_recommendations}]
        write_analysis_to_csv(analysis_data)
        for vacancy in unique_vacancies:
            try:
                await update.message.reply_text(
                    f"🔹 {vacancy['name']}\n"
                    f"🏢 Компания: {vacancy['Компания']}\n"
                    f"💰 Зарплата: {vacancy['Зарплата']}\n"
                    f"📍 Адрес: {vacancy['Адрес']}\n"
                    f"📑 Требования: {vacancy['Требования']}\n"
                    f"🔗 Ссылка: {vacancy['Ссылка']}",
                    parse_mode="Markdown", disable_web_page_preview=True)
            except Exception as e:
                logging.error(f"Ошибка при отправке вакансии: {e}")
        context.user_data['offset'] = offset + 1
    else:
        await update.message.reply_text("Нет новых вакансий.")

async def new_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    global offset_loadmore
    offset_loadmore = 0 
    if os.path.exists(VACANCIES_FILE):
        os.remove(VACANCIES_FILE)
    if os.path.exists(ANALYSIS_FILE):
        os.remove(ANALYSIS_FILE)
    
    context.user_data.clear()
    context.user_data['search_in_progress'] = False
    context.user_data['waiting_for_number'] = False
    context.user_data['vacancies'] = []
    await update.message.reply_text("Напишите вакансию, по которой вы хотите подобрать.")

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("analyze", analyze))
    application.add_handler(CommandHandler("load_more", load_more))
    application.add_handler(CommandHandler("new_search", new_search))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_query))

    application.run_polling()

if __name__ == '__main__':
    main()