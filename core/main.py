import telebot
import my_data
from datetime import datetime
import os 
from gtts import gTTS
from pytubefix import YouTube
from moviepy.editor import VideoFileClip, AudioFileClip


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




@bot.message_handler(commands=['youtube'])
def send_welcome(message):
    bot.reply_to(message, "welcome to youtube downloader bot")

@bot.message_handler(func= lambda message:True ,content_types=['text'])
def url_handler(message):
    url = message.text
    try:
        yt = YouTube(url)
        bot.reply_to(message, "select the quality", reply_markup=quality_markup(yt))
    except Exception as e:
        print(f"Error:{e}")
        bot.reply_to(message, "invalid youtube")
        

def quality_markup(yt):                
    markup = telebot.types.InlineKeyboardMarkup()
    streams = yt.streams.filter(mime_type = "video/mp4")
    
    for stream in streams:
        resolution = stream.resolution
        button_text = f"{resolution} - {stream.mime_type}"
        callback_data = f"{stream.itag}|{yt.watch_url}"
        button = telebot.types.InlineKeyboardButton(button_text, callback_data=callback_data)
        markup.add(button)
    return markup    


@bot.callback_query_handler(func= lambda call:True)
def handle_callback(call):
    itag, url = call.data.split('|')
    yt = YouTube(url)
    stream = yt.streams.get_by_itag(itag)
    video_filename = "video.mp4"
    audio_filename = "audio.mp4"
    final_filename = "final_video.mp4"
    
    stream.download(filename=video_filename)
    try:
        if not stream.is_progressive:
            audio_stream = yt.streams.filter(only_audio=True).first()
            audio_stream.download(filename=audio_filename)
            video_clip = VideoFileClip(video_filename)
            audio_clip = AudioFileClip(audio_filename)
            
            final_clip = video_clip.set_audio(audio_clip)
            final_clip.write_videofile(final_filename, codec='libx264')
            
            with open(final_filename, 'rb') as video:
                bot.send_video(call.message.chat.id, video)
                
            os.remove(video_filename)
            os.remove(audio_filename)
            os.remove(final_filename)
        else:
            with open(video_filename, 'rb') as video:
                bot.send_video(call.message.chat.id, video)
            os.remove(video_filename)
    except Exception as e:
        print(f"error sending file: {e}")
        bot.reply_to(call.message, "failed top send")


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
