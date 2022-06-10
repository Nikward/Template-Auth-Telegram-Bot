import telebot 
from telebot import apihelper
from telebot import types
import re
import xlsxwriter
from datetime import datetime, date, time

token='<yout_telegram_bot_token>'
keyboard1 = telebot.types.ReplyKeyboardMarkup()
keyboard1.row('Проверка связи', 'Авторизация')
keyboard1.row('Запрос')
bot=telebot.TeleBot(token)

IDS=[]  # id пользователей кто запустил бота
ALLOW_USERS = {
        "login1": "password1", 
        "login2": "password2"
    }

# Запуск бота
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Здравствуйте, Вы меня запустили!.\nПожалуйста, пройдите этап авторизации. Команда /login', reply_markup=keyboard1)

    """Запрос логина"""
    pass

@bot.message_handler(commands=['help'])
def author(message):
    text = """/start - Запуск бота
/help - Справка
/login - Авторизация
/your_command - Твоя команда. (На будущее можно будет добавить)

Доступные запросы:

type_request1 - Первый вид запроса (Имя)
type_request2 - Второй вид запроса (Почта)
type_request3 - Третий вид запроса (Номер)
...""" 
    bot.send_message(message.chat.id, text)

# Авторизация
@bot.message_handler(commands=['login'])
def save_login(message):
    msg = bot.send_message(message.chat.id, "Введите свой логин")
    bot.register_next_step_handler(msg, check_login)

def check_login(message):
    print('Присланный логин:', message.text)
    if message.text in ALLOW_USERS:
        print("Такой пользователь есть в списке допущенных лиц")
        msg = bot.send_message(message.chat.id, "Введите свой пароль")
        bot.register_next_step_handler(msg, check_password, message.text)
    else:
        print("Такого пользователя нет в списке допущенных лиц")
        bot.send_message(message.chat.id, "Такого пользователя не зарегистрировано")

def check_password(message, login):
    print('Присланный пароль:', message.text)
    if message.text == ALLOW_USERS[login]:
        IDS.append(message.chat.id) # Добавление id пользователя в массив авторизованных пользователей
        print("Пароль верный")
        bot.send_message(message.chat.id, f'Авторизация пройдена успешно. Бот в готовности принимать запросы от Вашего id: {message.chat.id}.\nПриятного пользования "{message.from_user.username}"')
    else:
        print("Пароль не верный")
        bot.send_message(message.chat.id, "Пароль не верный")
   
# Обработка сообщений
@bot.message_handler()
def handle_message(message):
    print(message.text)
    print(message.chat.id)
    print(message.from_user.username)
    if message.text=="Авторизация":
        save_login(message)
    elif message.text=="Проверка связи":
            bot.send_message(message.chat.id, f'Привет, {message.from_user.username}, я работаю, все ОК!', reply_markup=keyboard1)
    elif message.chat.id not in IDS:
        print("Данный пользователь не авторизован")
        bot.send_message(message.chat.id, "Для выполнения запросов необходима авторизация")
    else:
        if message.text=="Запрос":
            msg = bot.send_message(message.chat.id, "Пришлите вид запроса", reply_markup=keyboard1)
            bot.register_next_step_handler(msg, make_request)
        else: 
            bot.send_message(message.chat.id, 'Не знаю такую команду', reply_markup=keyboard1)

def make_request(message):
    if message.text == "type_request1":
        msg = bot.send_message(message.chat.id, "Пришлите параметр для запроса", reply_markup=keyboard1) # Номер телефона, почта, имя и т.п.
        bot.register_next_step_handler(msg, request1)
    elif message.text == "type_request2":
        msg = bot.send_message(message.chat.id, "Пришлите параметр для запроса", reply_markup=keyboard1) # Номер телефона, почта, имя и т.п.
        bot.register_next_step_handler(msg, request2)
    elif message.text == "type_request3":
        msg = bot.send_message(message.chat.id, "Пришлите параметр для запроса", reply_markup=keyboard1) # Номер телефона, почта, имя и т.п.
        bot.register_next_step_handler(msg, request3)
    else:
        msg = bot.send_message(message.chat.id, "Не знаю такого запроса") 

def request1(message):
    if valid_param1(message.text) == False:
        bot.send_message(message.chat.id, "Неверный параметр для данного вида запроса", reply_markup=keyboard1)
    else:
        data = Request_to_DB("REQUEST_SQL_1", message.text)
        # Create EXEL-файл 
        filename = "request1_exel.xlsx"
        Create_Exel(filename, data)
        # Send file to user
        f = open(filename,"rb")
        bot.send_document(message.chat.id,f)
        f.close()
        logging(message.from_user.username, 'request1', message.text)

def request2(message):
    if valid_param2(message.text) == False:
        bot.send_message(message.chat.id, "Неверный параметр для данного вида запроса", reply_markup=keyboard1)
    else:
        data = Request_to_DB("REQUEST_SQL_2", message.text)
        # Create EXEL-файл 
        filename = "request2_exel.xlsx"
        Create_Exel(filename, data)
        # Send file to user
        f = open(filename,"rb")
        bot.send_document(message.chat.id,f)
        f.close()
        logging(message.from_user.username, 'request1', message.text)

def request3(message):
    if valid_param3(message.text) == False:
        bot.send_message(message.chat.id, "Неверный параметр для данного вида запроса", reply_markup=keyboard1)
    else:
        data = Request_to_DB("REQUEST_SQL_3", message.text)
        # Create EXEL-файл 
        filename = "request3_exel.xlsx"
        Create_Exel(filename, data)
        # Send file to user
        f = open(filename,"rb")
        bot.send_document(message.chat.id,f)
        f.close()
        logging(message.from_user.username, 'request1', message.text)

def valid_param1(param):
    # Проверка правильности параметра ... (если должны быть  цифры, то цифры и т.д.)
    return True

def valid_param2(param):
    # Проверка правильности параметра ... (если должны быть  цифры, то цифры и т.д.)
    return True

def valid_param3(param):
    # Проверка правильности параметра ... (если должны быть  цифры, то цифры и т.д.)
    return True

def Create_Exel(filename, data):
    # открываем новый файл на запись
    workbook = xlsxwriter.Workbook(filename)
    # создаем там "лист"
    worksheet = workbook.add_worksheet()
    # в ячейку A1 пишем текст
    worksheet.write('A1', data)
    # сохраняем и закрываем
    workbook.close()

def Request_to_DB(REQUEST_SQL, param):
    # Имитация выполнения запроса к БД
    responce = f'responce_{REQUEST_SQL}_{param}'
    return responce

def logging(username, request, param):
    datetime_ = datetime.now()
    log_string = f'{datetime_}. USER: {username}, REQUEST: {request}, PARAMETR: {param}.\n'
    f = open('log.txt' , 'a')
    f.write(log_string)
    f.close()

if __name__ == "__main__":  
    bot.polling()  # запуск бота (блокирующий вызов)
    # Отправка всем уведомления о выключении
    for id in IDS:
        bot.send_message(id, 'Я временно выключаюсь...')
    print("Бот отключен")
    

