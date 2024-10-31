import requests

# Функция для поиска вакансий через API hh.ru
def get_hh_vacancies(query="информационная безопасность", region=1):
    url = "https://api.hh.ru/vacancies"
    
    # Параметры для поиска вакансий
    params = {
        "text": query,  # Ключевое слово для поиска
        "area": region,  # Регион (1 — Москва, 113 — Россия)
        "per_page": 5,  # Количество вакансий на странице (для примера берем 5)
    }
    
    # Отправляем GET-запрос к API
    response = requests.get(url, params=params)
    
    # Проверяем успешность запроса
    if response.status_code == 200:
        vacancies = response.json()['items']  # Получаем список вакансий
        results = []

        for vacancy in vacancies:
            title = vacancy['name']  # Название вакансии
            salary = vacancy.get('salary')
            if salary:
                salary_from = salary['from'] if salary['from'] else 'не указана'
                salary_to = salary['to'] if salary['to'] else 'не указана'
                salary_currency = salary['currency']
                salary_str = f"{salary_from} - {salary_to} {salary_currency}"
            else:
                salary_str = "Зарплата не указана"
            
            employer = vacancy['employer']['name']  # Название компании
            link = vacancy['alternate_url']  # Ссылка на вакансию
            
            # Добавляем вакансию в список
            results.append({
                "title": title,
                "salary": salary_str,
                "employer": employer,
                "link": link
            })

        return results
    else:
        print(f"Ошибка при запросе: {response.status_code}")
        return None

# Пример использования функции
vacancies = get_hh_vacancies()

if vacancies:
    for v in vacancies:
        print(f"Вакансия: {v['title']}\nЗарплата: {v['salary']}\nКомпания: {v['employer']}\nСсылка: {v['link']}\n")