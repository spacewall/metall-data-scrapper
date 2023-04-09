import csv
import lxml
import random
from time import sleep
import json
from pyfiglet import Figlet as fi
from bs4 import BeautifulSoup
import requests
import os

def get_data(listing_url, headers):
    print("[*] UPDATE HTML FILES")
    print("[*] Total: 10 pages")
    try:
        # Спарсим данные с каждой страницы
        for item in range(1, 11):
            print(f"[*] Loading page #{item}")
            page = str(item)
            url = listing_url + page
            req = requests.get(url=url, headers=headers)
            src = req.text

            # Зададим задержку
            sleep(random.random())

            # Сохраним данные со страницы в html файл
            with open(f"page_#{item}.html", "w") as file:
                file.write(src)
                print(f"[*] Page #{item} has been successfully saved. {10 - item} left...")
    except requests.ConnectionError as er:
            print("[!] Connection is failed. Please check your connection")

def get_links():
    print("[*] UPDATE JSON FILES")
    print("[*] Total: 10 files")
    # Прочитаем файлы с данными страниц
    for num in range(1, 11):
        try:
            file = open(f"page_#{num}.html", "r")
            src = file.read()
            file.close()
        except FileNotFoundError:
            print("[!] Please update data from source")
            break
        
        # Выделим нужные блоки данных
        soup = BeautifulSoup(src, "lxml")
        
        # Извлечём табицу с ссылками на информацию о каждой марке металла
        table = soup.find("table", width="100%", border="0", cellpadding="2", cellspacing="2").\
            find_next_sibling()
        data = table.find_next_sibling().find_all("tr")

        # Запишем данные о марках в словарь
        all_metall_grades = dict()
        for item in data:
            head = item.find("a").text
            href = item.find("a").get("href")
            exceptions_ = [
                "Марки стали и сплавы",
                "Бронзовый круг БрАЖМц10-3-1,5 и его применение",
                "Баббиты",
                "Бронза сплавы и марки",
                "Латунь сплавы и марки",
                "Марки чугуна",
                "Алюминий сплавы и марки",
                "Магний",
                "Медь сплавы и марки",
                "Сталь нержавеющая (коррозионно-стойкая)",
                "Свинец сплавы и марки",
                "Сталь специального назначения",
                "Никель сплавы и марки",
                "Сталь электротехническая",
                "Сталь конструкционная",
                "Стальной сплав прецизионный",
                "Олово сплавы и марки",
                "Титан сплав и марки",
                "Цинк сплавы и марки"
            ]
            if head in exceptions_:
                continue
            else:
                all_metall_grades[head] = "http:" + href

        # Зададим задержку
        sleep(random.random())

        # Запишем данные в json файл
        with open(f"page_#{num}.json", "w") as file:
            json.dump(all_metall_grades, file, ensure_ascii=False, indent=4)
            print(f"[*] Page #{num} has been successfully saved. {10 - num} left...")

def save_data(headers):
    print("[*] SAVE METALL GRADES")
    # Прочитаем json файл
    for num in range(1, 11):
        print(f"[*] Loading page #{num}")
        with open(f"page_#{num}.json", "r") as file:
            all_metall_grades = json.load(file)

        length = len(all_metall_grades.items())
        print(f"[*] Total: {length} metall grades")

        # Получим данные по ссылкам о каждой марке металла
        for head, href in all_metall_grades.items():
            # Преобразуем заговолвки
            head = head.replace(" ", "_")

            # Спарсим даные по ссылке
            try:
                req = requests.get(url=href, headers=headers)
                src = req.text
            except requests.ConnectionError as er:
                print("[!] Connection is failed. Please check your connection")
            
            soup = BeautifulSoup(src, "lxml")
            table = soup.find("table", class_="marochn").find("tbody").\
                find_all("tr")
            
            # Удалим елементы списка с заголовком таблицы и последним химическим элементом
            table.pop(0)
            table.pop()

            # Запишем данные в csv файл
            if not os.path.exists("data"):
                os.mkdir("data")
            
            with open(f"data/{head}.csv", 'w') as file:
                # Внесём заголовки в таблицу
                writer = csv.writer(file)
                writer.writerow(["Element", "Min_value", "Max_value"])

                # Преобразуем таблицу
                for item in table:
                    # Устраним ненужные символы в строках
                    item_text = item.text
                    if "до" in item_text:
                        item_text = item_text.replace("до", "0")
                    elif "-" in item_text:
                        item_text = item_text.replace("-", "")
                    
                    # Запишем строку
                    writer.writerow(item_text.split())
            
            # Зададим задержку
            sleep(random.randrange(1, 3, 1))

            length -= 1
            print(f"[*] Metall grade {head} has been successfully saved. {length} left...")
        print(f"[*] Metall grades from page #{num} has been successfully saved as scv files. {10 - num} left...")
    print("[*] All metall grades have been successfully saved!")

def main():
    preview_text = fi(font='slant')
    print(preview_text.renderText('METALL DATA SCRAPPER'))
    # Получим/обновим даные с сайта по выбору пользователя
    flag = input("[?] Do you want to write/update data from source? Print y to update or any command to pass: ")

    if flag == "y":
        headers = {
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)\
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.167 YaBrowser/22.7.3.799 Yowser/2.5 Safari/537.36"
        }
        url = "https://metallicheckiy-portal.ru/marki_metallov/search/?sks=&levelyr=&gid=&page="
        get_data(listing_url=url, headers=headers)
        get_links()
        save_data(headers)
    else:
        print("[*] Bye!")

if __name__ == "__main__":
    main()