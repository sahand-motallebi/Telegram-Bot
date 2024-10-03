import telebot
import my_data
from datetime import datetime
import os 


API_TOKEN = os.environ.get('API_TOKEN')

bot = telebot.TeleBot(API_TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Please enter your first name:")


@bot.message_handler(func=lambda message: message.text and not user_data.get('first_name'))
def handle_first_name(message):
    user_data['first_name'] = message.text
    bot.reply_to(message, "Please enter your last name:")


@bot.message_handler(func=lambda message: message.text and user_data.get('first_name') and not user_data.get('last_name'))
def handle_last_name(message):
    user_data['last_name'] = message.text
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = my_data.connection()
    my_data.add_user(conn, user_data['first_name'], user_data['last_name'], current_time)
    my_data.close_connection(conn)

    bot.reply_to(message, f"Thanks {user_data['first_name']} {user_data['last_name']}, your information has been saved!")

if __name__ == '__main__':
    conn = my_data.connection()
    my_data.sql_table(conn)
    my_data.close_connection(conn)
    bot.infinity_polling()
