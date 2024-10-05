# import telebot
# from pytubefix import YouTube
# import os 
# from moviepy.editor import VideoFileClip, AudioFileClip

# API_TOKEN = os.environ.get('API_TOKEN')
# bot = telebot.TeleBot(API_TOKEN)

# @bot.message_handler(commands=['youtube'])
# def send_welcome(message):
#     bot.reply_to(message, "welcome to youtube downloader bot")

# @bot.message_handler(func= lambda message:True ,content_types=['text'])
# def url_handler(message):
#     url = message.text
#     try:
#         yt = YouTube(url)
#         bot.reply_to(message, "select the quality", reply_markup=quality_markup(yt))
#     except Exception as e:
#         print(f"Error:{e}")
#         bot.reply_to(message, "invalid youtube")
        

# def quality_markup(yt):                
#     markup = telebot.types.InlineKeyboardMarkup()
#     streams = yt.streams.filter(mime_type = "video/mp4")
    
#     for stream in streams:
#         resolution = stream.resolution
#         button_text = f"{resolution} - {stream.mime_type}"
#         callback_data = f"{stream.itag}|{yt.watch_url}"
#         button = telebot.types.InlineKeyboardButton(button_text, callback_data=callback_data)
#         markup.add(button)
#     return markup    


# @bot.callback_query_handler(func= lambda call:True)
# def handle_callback(call):
#     itag, url = call.data.split('|')
#     yt = YouTube(url)
#     stream = yt.streams.get_by_itag(itag)
#     video_filename = "video.mp4"
#     audio_filename = "audio.mp4"
#     final_filename = "final_video.mp4"
    
#     stream.download(filename=video_filename)
#     try:
#         if not stream.is_progressive:
#             audio_stream = yt.streams.filter(only_audio=True).first()
#             audio_stream.download(filename=audio_filename)
#             video_clip = VideoFileClip(video_filename)
#             audio_clip = AudioFileClip(audio_filename)
            
#             final_clip = video_clip.set_audio(audio_clip)
#             final_clip.write_videofile(final_filename, codec='libx264')
            
#             with open(final_filename, 'rb') as video:
#                 bot.send_video(call.message.chat.id, video)
                
#             os.remove(video_filename)
#             os.remove(audio_filename)
#             os.remove(final_filename)
#         else:
#             with open(video_filename, 'rb') as video:
#                 bot.send_video(call.message.chat.id, video)
#             os.remove(video_filename)
#     except Exception as e:
#         print(f"error sending file: {e}")
#         bot.reply_to(call.message, "failed top send")

# bot.infinity_polling()                                      