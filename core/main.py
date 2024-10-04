import telebot
import my_data
from datetime import datetime
import os 
from gtts import gTTS
import requests

API_TOKEN = os.environ.get('API_TOKEN')

bot = telebot.TeleBot(API_TOKEN)

user_data = {}

# ایجاد پوشه‌های لازم
if not os.path.exists("downloads"):
    os.makedirs("downloads")
if not os.path.exists("voices"):
    os.makedirs("voices")

DOWNLOAD_DIR = "downloads/"

@bot.message_handler(commands=['start'])
def ask_for_info(message):
    user_id = message.from_user.id    
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
    my_data.close_connection(conn)

# هندلر دانلود فایل‌های MP3 و MP4
def download_file(url):
    local_filename = url.split('/')[-1]
    
    if local_filename.endswith('.mp3') or local_filename.endswith('.mp4'):
        file_path = os.path.join(DOWNLOAD_DIR, local_filename)

        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            return file_path
        except requests.exceptions.RequestException as e:
            return None
    else:
        return None

@bot.message_handler(commands=['download'])
def ask_for_url(message):
    bot.reply_to(message, "Please send a valid MP3 or MP4 URL.")

@bot.message_handler(func=lambda message: message.text.startswith('http'))
def handle_message(message):
    url = message.text
    bot.send_message(message.chat.id, "File is downloading...")
    file_path = download_file(url)

    if file_path:
        with open(file_path, 'rb') as f:
            bot.send_document(chat_id=message.chat.id, document=f)
        os.remove(file_path)
    else:
        bot.reply_to(message, "Invalid URL or file format. Please send a valid MP3 or MP4 URL.")

@bot.message_handler(commands=['voice'])
def send_voice_prompt(message):
    bot.send_message(message.chat.id, "Send me a text and I will read it for you in English.")

@bot.message_handler(func=lambda message: not message.text.startswith('http') and message.text)
def text_to_speech(message):
    text = message.text
    file_name = "voices/output.mp3"
    output = gTTS(text=text, lang="en", tld='com.au')
    output.save(file_name)
    bot.send_voice(chat_id=message.chat.id, reply_to_message_id=message.id, voice=open(file_name, "rb"))
    os.remove(file_name)

if __name__ == '__main__':
    conn = my_data.connection()
    my_data.sql_table(conn)
    my_data.close_connection(conn)
    bot.infinity_polling()
