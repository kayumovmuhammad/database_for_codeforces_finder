from bs4 import BeautifulSoup as bs
import cloudscraper
from time import sleep
import json

import requests
from config import *

# читаем данные из файла(не всегда)
with open('data.json', 'r') as file:
    data = json.loads(file.read())
    

print("Начинаем доставать все хэндлы(это может занять несколько десятков минут)...")

scraper = cloudscraper.create_scraper()
url = "https://codeforces.com/ratings/page/"

ind = 781
page_cnt = ind
firstTime = True

# делаем цикл через while т.к. будем обновлять page_cnt
while ind <= page_cnt:
    try:
        # берём информацию из страниц номер страница ind
        answer = scraper.get(f"{url}{ind}")
        users = []
        soup = bs(answer.content, 'html5lib')
        if firstTime:
            # если мы на первой странице то нужно взять информацию о количестве страниц
            pagination = soup.find('div', {'class' : 'pagination'})
            cnt_link = pagination.find_all('a')[-2]
            page_cnt = int(cnt_link.text)
            firstTime = False
        
        # в users у нас хранятся все хэндлы
        table = soup.find('div', {'class': 'datatable ratingsDatatable'})
        part_users = table.find_all('a', {'class': 'rated-user'})

        for j in part_users:
            users.append((j.text))
            
        # через codeforces api мы берём данные об фамилии и имени каждого человека
        api_url = 'https://codeforces.com/api/user.info?handles='
        for user in users:
            api_url += f'{user};'
         
        req = scraper.get(api_url)

        ans = dict(req.json())['result']
        for user in ans:
            try:
                # записываем данные в data в виде { 'фамилия' : { 'имя' , [ хэндлы ] } }
                handle = user['handle']
                name = user['firstName'].lower()
                surname = user['lastName'].lower()
                if (surname in data):
                    if (name in data[surname]):
                        if (handle not in data[surname][name]):
                            data[surname][name].append(handle)
                    else:
                        data[surname][name] = [handle]
                else:
                    data[surname] = {name: [handle]}
            except:
                pass 
        
        print(f"Страница {ind} ✅")
    except Exception as e:
        message = f"Ошибка на странице {ind}: {e}"
        send_message_url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
        payload = {
            'chat_id': ADMIN_CHAT_ID,
            'text': message
        }
        print(f"Ошибка на странице {ind}: {e}")
        response = requests.post(send_message_url, data=payload)
        break
    ind += 1
    
    
print("Записываем данные")

# записываем данные в файл
with open('data.json', 'w') as file:
    file.write(json.dumps(data))
