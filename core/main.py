import telebot
import my_data
from datetime import datetime
import os 
from gtts import gTTS

API_TOKEN = os.environ.get('API_TOKEN')

bot = telebot.TeleBot(API_TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def ask_for_info(message):
    user_id = message.from_user.id
    
    # ارتباط با دیتابیس
    conn = my_data.connection()

    if my_data.user_exists(conn, user_id):
        bot.reply_to(message, "You have already registered!")
    else:
        bot.reply_to(message, "Please enter your first name:")
        bot.register_next_step_handler(message, get_first_name)

    my_data.close_connection(conn)


def get_first_name(message):
    first_name = message.text
    bot.reply_to(message, "Please enter your last name:")
    bot.register_next_step_handler(message, get_last_name, first_name)

def get_last_name(message, first_name):
    last_name = message.text
    user_id = message.from_user.id
    hire_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = my_data.connection()

    my_data.add_user(conn, user_id, first_name, last_name, hire_date)
    bot.reply_to(message, "Your information has been saved successfully!")

    # بستن ارتباط با دیتابیس
    my_data.close_connection(conn)
    
    
@bot.message_handler(commands=['voice'])
def send_welcome(message):
    bot.send_message(
        message.chat.id, "Send me a text and i will read it for you in english")
    

@bot.message_handler(func=lambda message: True)
def text_to_speech(message):
    text= message.text
    file_name = "voices/output.mp3"
    output = gTTS(text=text, lang="en",tld='com.au')
    output.save(file_name)
    bot.send_voice(chat_id=message.chat.id,reply_to_message_id=message.id,voice=open(file_name,"rb"))
    os.remove(file_name)


if __name__ == '__main__':
    conn = my_data.connection()
    my_data.sql_table(conn)
    my_data.close_connection(conn)
    bot.infinity_polling()
