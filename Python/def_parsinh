import requests
from bs4 import BeautifulSoup

city_number = (
    {}
)  # Я словари ещё не прошёл блин, не могу ассоциации по номерам простроить, скоро уже пройду.

url = f"https://dreamjob.ru/vakansii?jbfrp[text]=%D0%B8%D0%BD%D1%84%D0%BE%D1%80%D0%BC%D0%B0%D1%86%D0%B8%D0%BE%D0%BD%D0%BD%D0%B0%D1%8F%20%D0%B1%D0%B5%D0%B7%D0%BE%D0%BF%D0%B0%D1%81%D0%BD%D0%BE%D1%81%D1%82%D1%8C"
response = requests.get(url).text
soup = BeautifulSoup(response, "lxml")
block = soup.find("div", class_="vacancies-new__list")

vacancy_list = block.find_all("h4", class_="vacancy-new__heading")
href = block.find_all(class_="vacancy-new__main-link", href=True)
previous = block.find_all("p", class_="vacancy-new__text-preview")

for i in range(len(href)):
    print(vacancy_list[i].text)
    print("https://dreamjob.ru", href[i].get("href"), sep="")
    print(previous[i].text)
    print()
