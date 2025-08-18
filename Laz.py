import random
import time
import requests
from colorama import *
import json
import os

init()

#тут меню если что
print(Fore.LIGHTMAGENTA_EX + """
██╗░░░░░░█████╗░███████╗      
██║░░░░░██╔══██╗╚════██║       
██║░░░░░███████║░░███╔═╝       
██║░░░░░██╔══██║██╔══╝░░       
███████╗██║░░██║███████╗    
╚══════╝╚═╝░░╚═╝╚══════╝     
Разраб: @Noo1us


""" + Style.RESET_ALL)

# Настройки бота
TOKEN = "7609829962:AAEkPAE7kPI_aQdVKj3R34ekeLPwVak80Nw"
URL = f"https://api.telegram.org/bot{TOKEN}/"
last_update_id = 0

# Настройки канала
CHANNEL_ID = "@Rako_laz"  # Замените на username вашего канала
CHANNEL_LINK = "https://t.me/Rako_laz"  # Замените на ссылку вашего канала

# Файл для хранения данных
DATA_FILE = "user_data.json"

# Загрузка данных из файла при старте
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

# Сохранение данных в файл
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# База данных (загружается из файла)
user_data = load_data()

# Варианты исходов
positive = [
    ("Ты залез в бб:", 1),
    ("Ты залез в теплотрассу:", 1),
    ("Ты залез в зб завод:", 2),
    ("Ты залез в кабельник:", 3),
    ("Ты нашел ящики гп-5:", 5),
    ("Ты нашел ящики гп-7:", 10),
    ("Ты нашел ящики хомяков:", 10),
    ("Руфанул мск сити:", 20),
    ("Сбежал от чопа:", 10),
    ("Нашел пк в зб:", 10),
    ("Залез в дельту:", 10),
    ("Залез в мясокомбинат:", 2),
    ("Ты пролез в райеник:", 15)
]

negative = [
    ("Тебя поймал ЧОП:", -2),
    ("Тебя спалила бабка:", -1),
    ("Ты застрял в узком ракоходе:", -3),
    ("Тебя забрали в ментовку:", -5),
    ("Ты потерял все гп-5:", -4),
    ("Ты потерял фонарик:", -2),
    ("Сжег высел:", -10),
    ("Мама наругала за руфы:", -15),
    ("Сорвался с руфа:", -10),
    ("Порезался на руфе:", -10),
    ("Тебя закрыли в бб:", -10),
    ("Тебя унесло течение в левневке:", -20),
    ("Ты задохнулся в теплотрассе:", -20)
]

def get_updates():
    global last_update_id
    url = URL + f"getUpdates?offset={last_update_id + 1}"
    response = requests.get(url).json()
    return response.get("result", [])

def send_message(chat_id, text, reply_markup=None):
    url = URL + f"sendMessage?chat_id={chat_id}&text={text}"
    if reply_markup:
        url += f"&reply_markup={reply_markup}"
    requests.get(url)

def is_user_subscribed(user_id):
    # Проверяем подписку пользователя на канал
    url = URL + f"getChatMember?chat_id={CHANNEL_ID}&user_id={user_id}"
    response = requests.get(url).json()
    return response.get("result", {}).get("status") in ["member", "administrator", "creator"]

def handle_updates(updates):
    global last_update_id, user_data
    
    for update in updates:
        last_update_id = update["update_id"]
        
        if "message" not in update:
            continue
            
        message = update["message"]
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        text = message.get("text", "")
        
        if not text.startswith("/"):
            continue
            
        command = text.split()[0].lower()
        
        if command == "/start":
            welcome_text = (
                "Привет! Это игра в Раколаз\n\n"
                "Доступные команды:\n"
                "/Laz - начатт лазать\n"
                "/Lazs - посмотреть свой счет\n\n"
                "ъ?"
            )
            
            # Проверяем подписку
            if not is_user_subscribed(user_id):
                keyboard = {
                    "inline_keyboard": [[
                        {"text": "Подписаться на канал", "url": CHANNEL_LINK},
                        {"text": "Я подписался", "callback_data": "check_sub"}
                    ]]
                }
                send_message(chat_id, welcome_text, reply_markup=json.dumps(keyboard))
            else:
                send_message(chat_id, welcome_text)
                
        elif command == "/laz":
            # Проверяем подписку перед выполнением команды
            if not is_user_subscribed(user_id):
                send_message(chat_id, f"Сначала подпишись на канал: {CHANNEL_LINK}")
                continue
                
            current_time = time.time()
            
            if str(user_id) not in user_data:
                user_data[str(user_id)] = {
                    "laz_count": 0,
                    "last_laz_time": 0
                }
            
            last_used = user_data[str(user_id)].get("last_laz_time", 0)
            if current_time - last_used < 360:
                remaining_time = 360 - int(current_time - last_used)
                minutes = remaining_time // 60
                seconds = remaining_time % 60
                send_message(chat_id, f"Подожди еще {minutes} минут {seconds} секунд перед следующим использованием!")
                continue
            
            if random.random() < 0.7:
                outcome, points = random.choice(positive)
            else:
                outcome, points = random.choice(negative)
            
            user_data[str(user_id)]["laz_count"] += points
            user_data[str(user_id)]["last_laz_time"] = current_time
            save_data(user_data)  # Сохраняем данные после изменения
            
            response = f"{outcome}\n"
            if points > 0:
                response += f"+{points} к лазам!\n"
            else:
                response += f"{points} к лазам...\n"
            response += f"Текущий счет: {user_data[str(user_id)]['laz_count']}"
            
            send_message(chat_id, response)
            
        elif command == "/lazs":
            # Проверяем подписку перед выполнением команды
            if not is_user_subscribed(user_id):
                send_message(chat_id, f"Сначала подпишись на канал: {CHANNEL_LINK}")
                continue
                
            if str(user_id) in user_data:
                send_message(chat_id, f"Твой счет: {user_data[str(user_id)]['laz_count']}")
            else:
                send_message(chat_id, "Используй /Laz чтобы начать!")
                
        # Админ-команды
        elif command == "/loxd":
            try:
                password = text.split()[1]
                if password == "Rassa_12":
                    user_id = message["from"]["id"]
                    user_data[str(user_id)] = {"laz_count": 0, "is_admin": True}
                    save_data(user_data)  # Сохраняем данные после изменения
                    send_message(chat_id, "Админ-панель активирована!\nИспользуй /set_laz <число>")
                else:
                    send_message(chat_id, "Неверный пароль!")
            except IndexError:
                send_message(chat_id, "Используй: /LoxD пароль")
                
        elif command == "/set_laz":
            user_id = message["from"]["id"]
            if str(user_id) in user_data and user_data[str(user_id)].get("is_admin"):
                try:
                    new_value = text.split()[1]
                    try:
                        user_data[str(user_id)]["laz_count"] = int(new_value)
                    except ValueError:
                        user_data[str(user_id)]["laz_count"] = new_value
                    save_data(user_data)  # Сохраняем данные после изменения
                    send_message(chat_id, f"Счет изменен: {user_data[str(user_id)]['laz_count']}")
                except IndexError:
                    send_message(chat_id, "Используй: /set_laz <значение>")
            else:
                send_message(chat_id, "Нет прав!")

def main():
    print(Fore.GREEN + "Бот запущен..." + Style.RESET_ALL)
    while True:
        try:
            updates = get_updates()
            if updates:
                handle_updates(updates)
            time.sleep(1)
        except Exception as e:
            print(Fore.RED + f"Ошибка: {e}" + Style.RESET_ALL)
            time.sleep(5)

if __name__ == "__main__":
    main()
