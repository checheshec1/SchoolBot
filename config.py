import telebot

#Подключение к телеграм-боту
BOT_API = ('5081050812:AAFYu2xRgwxCFmBSEdtMhMw-TpitwOmME8A')
bot = telebot.TeleBot(BOT_API)

#Подключение к БД
connectionString = ("DRIVER=SQL Server;""SERVER=LAPTOP-F1U02MM4\SQLEXPRESS;"
                    "Database=TurkishSchool;""Trusted_Connection=yes")