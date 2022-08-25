import nltk
import pyodbc
from telebot import types
import random
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import datetime
import config
import NLP
import wiki

#Подключение к телеграм-боту
bot = config.bot

name = ''
surname = ''
phone = ''
date = ''
month31 = [1, 3, 5, 7, 8, 10, 12]
welcome_response = ['привет', 'здравствуйте', 'доброго времени суток', 'здорова']

text_commands = ['информация о школе', 'о турецком языке', 'наши преподаватели', 'тарифы', 'сайт', 'instagram',
                 'записаться на курс', 'записаться на пробное занятие']

data = open("D:\Pythonlab\SchoolBot\ScoolInfo.txt", 'r', encoding='utf-8')
raw = data.read()
data.close()
sent_tokens = nltk.sent_tokenize(raw, 'russian')#Токенизация по предложениям

def generateResponse(user_question, message):
    bot_response = ''
    sent_tokens.append(user_question)
    TfidfVec = TfidfVectorizer(tokenizer=NLP.Normalize, stop_words=stopwords.words('russian'))
    tfidf = TfidfVec.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1], tfidf)
    idx = vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]
    if req_tfidf != 0:
        if user_question:
            bot_response = bot_response + sent_tokens[idx]
            return bot_response
    else:
        return message.chat.first_name + ', в данный момент я не располагаю данной информацией. Попробуйте позже.'

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, random.choice(welcome_response) + ' ' + message.chat.first_name + ', чем я могу помочь?')

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttoninfo = types.KeyboardButton("Информация о школе")
    buttonInfoLanguage = types.KeyboardButton('О Турецком языке')
    buttonTeachers = types.KeyboardButton('Наши преподаватели')
    buttonPrice = types.KeyboardButton('Тарифы')
    buttonSite = types.KeyboardButton('Сайт')
    buttonInstagram = types.KeyboardButton('Instagram')
    buttonTrial = types.KeyboardButton('Записаться на пробное занятие')
    buttonBuy = types.KeyboardButton('Записаться на курс')
    keyboard.add(buttoninfo, buttonInfoLanguage, buttonTeachers, buttonPrice, buttonInstagram, buttonSite, buttonBuy, buttonTrial)
    bot.send_message(message.chat.id, 'Выберите необходимый вам вариант или зайдайте свой вопрос', reply_markup=keyboard)

@bot.message_handler(content_types=['text'])
def message_about_school(message):
    exit = ['до свидания', 'пока', 'до завтра', 'до слудющего раза']
    exit_response = ['До свидания', 'Удачи', 'До встречи']
    if message.text.lower() in text_commands:
        if message.text.lower() == text_commands[0]:
            file = open("D:\Pythonlab\SchoolBot\AboutScool.txt", 'r', encoding='utf-8')
            bot.send_message(message.chat.id, file.read())
            file.close()
        elif message.text.lower() == text_commands[1]:
            bot.send_message(message.chat.id, wiki.wiki_data('Турецкий язык'))
        elif message.text.lower() == text_commands[2]:
            bot.send_message(message.chat.id, 'Наши преподаватели:\n' + getProfessors())
        elif message.text.lower() == text_commands[3]:
            bot.send_message(message.chat.id, 'Тарифы:\n' + getPrices())
        elif message.text.lower() == text_commands[4]:
            bot.send_message(message.chat.id, 'Наш сайт\n https://malinovaschool.ru/')
        elif message.text.lower() == text_commands[5]:
            bot.send_message(message.chat.id, 'Наш Instagram\n https://www.instagram.com/malinova_school')
        elif message.text.lower() == text_commands[6]:
            bot.send_message(message.chat.id, 'Записаться на курс можно на нашем сайте\n https://malinovaschool.ru/p/759ce0/')
        elif message.text.lower() == text_commands[7]:
            bot.send_message(message.chat.id, 'Регистрация на пробное занятие!')
            start(message)
    elif message.text.lower() in welcome_response:
        bot.send_message(message.chat.id, random.choice(welcome_response))
    elif message.text.lower() in exit:
        bot.send_message(message.chat.id, random.choice(exit_response) + ', ' + message.chat.first_name)
    else:
        bot.send_message(message.chat.id, generateResponse(message.text, message))

def getProfessors():
    connection = pyodbc.connect(config.connectionString, autocommit=True)
    cursor = connection.cursor()
    request = 'SELECT fname, mname, description FROM Professors'
    cursor.execute(request)
    text = ''
    counter = 1
    while 1:
        s = cursor.fetchone()
        if not s:
            connection.close()
            return text
        text = text + '\n{0}) {1} {2} ({3})'.format(counter, s.fname, s.mname, s.description)
        counter += 1

def getPrices():
    connection = pyodbc.connect(config.connectionString, autocommit=True)
    cursor = connection.cursor()
    request = 'SELECT Description, Price FROM Prices'
    cursor.execute(request)
    text = ''
    counter = 1
    while 1:
        s = cursor.fetchone()
        if not s:
            connection.close()
            return text
        text = text + '\n{0}) {1} - {2}₽)'.format(counter, s.Description, round(s.Price))
        counter += 1

def addDataBase(message):
    global name, surname, phone, date
    connection = pyodbc.connect(config.connectionString, autocommit=True)
    testRequest = ("SELECT FirstName, MiddleName FROM TrialLesson WHERE FirstName = '{0}' AND MiddleName = '{1}'".
                   format(name, surname))
    testRequest2 = ("SELECT LessonDate FROM TrialLesson WHERE FirstName = '{0}' AND MiddleName = '{1}' AND PhoneNuber = '{2}'".
                    format(name, surname, phone))
    requestString = ("INSERT INTO TrialLesson VALUES ('{0}', '{1}', '{2}', '{3}')".format(name, surname, phone, date))
    dbCursor = connection.cursor()
    dbCursor.execute(testRequest)
    ROW = dbCursor.fetchone()

    if ROW:
        bot.send_message(message.chat.id, 'Вы уже были зарегестрированы на пробное занятие!')
    else:
        dbCursor.execute(requestString)
        connection.commit()
        dbCursor.execute(testRequest2)
        row = dbCursor.fetchone()
        bot.send_message(message.chat.id, 'Вы успешно зарегестрированы на пробное занятие {0}!\n'
                                          'В течение суток с вами свяжутся для обсуждения деталей и уточнения времени.'.
                         format((str)(row.LessonDate)))
    connection.close()
    name = ''
    surname = ''
    phone = ''
    date = ''
    bot.register_next_step_handler(message, message_about_school)

def start(message):
    bot.send_message(message.chat.id, 'Напишите свое имя')
    bot.register_next_step_handler(message, getName)

def getName(message):
    global name
    name = message.text
    bot.send_message(message.chat.id, 'Напишите свою фамилию')
    bot.register_next_step_handler(message, getSurname)

def getSurname(message):
    global surname, phone
    surname = message.text
    bot.send_message(message.chat.id, 'Напишите свой телефон в формате 89*********')
    bot.register_next_step_handler(message, getPhone)

def getPhone(message):
    global phone
    phone = message.text
    bot.send_message(message.chat.id, 'Введите желаемые дату занятия в формате ДД.ММ.ГГГ')
    bot.register_next_step_handler(message, getDate)

def getDate(message):
    global date
    count = 0
    str = message.text
    list = str.split('.')

    if int(list[2]) >= int(datetime.datetime.now().year):
        if int(list[1]) <= 12 and int(list[1]) in month31 and int(list[1]) >= int(datetime.datetime.now().month):
            if int(list[0]) <= 31 and int(list[0]) > int(datetime.datetime.now().day):
                date = list[2] + '-' + list[1] + '-' + list[0]
                count = 1
            else:
                bot.send_message(message.chat.id, 'Введите корректную дату в формате ДД-ММ-ГГГГ')
                bot.register_next_step_handler(message, getDate)
        elif int(list[1]) <= 12 and int(list[1]) not in month31 and int(list[1]) >= int(datetime.datetime.now().month):
            if int(list[0]) <= 30 and int(list[0]) > int(datetime.datetime.now().day):
                date = list[2] + '-' + list[1] + '-' + list[0]
                count = 1
            else:
                bot.send_message(message.chat.id, 'Введите корректную дату в формате ДД.ММ.ГГГГ')
                bot.register_next_step_handler(message, getDate)
        else:
            bot.send_message(message.chat.id, 'Введите корректную дату в формате ДД.ММ.ГГГГ')
            bot.register_next_step_handler(message, getDate)
    else:
        bot.send_message(message.chat.id, 'Введите корректную дату в формате ДД.ММ.ГГГГ')
        bot.register_next_step_handler(message, getDate)

    if count == 1:
        kb = types.InlineKeyboardMarkup()
        key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
        key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
        kb.add(key_yes, key_no)
        bot.send_message(message.chat.id, text=('Проверьте введенные данные\nИмя: {0}\nФамилия: {1}\nТелефон: {2}\n'
                                                'Дата занятия: {3}'.format(name, surname, phone, date)),
                         reply_markup=kb)

@bot.callback_query_handler(func=lambda call: True)
def callback_Worker(call):
    if call.data == 'yes':
        bot.send_message(call.message.chat.id, 'Пожалуйста, подождите!')
        addDataBase(call.message)
    elif call.data == 'no':
        bot.send_message(call.message.chat.id, 'Ошибка регистрации. Повторите снова!')


bot.polling(none_stop=True, interval=0)