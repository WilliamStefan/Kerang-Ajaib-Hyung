import random
import telebot

answers = ["Ya", "Nggak"] # Jawaban si bot Kerang Ajaib Hyung

# Token si bot Kerang Ajaib Hyung
API_KEY = '1818338059:AAEzMAp6IMeZcJZPN_mV5-Qg3jXcTFY46Uk'
bot = telebot.TeleBot(API_KEY)

@bot.message_handler(func=lambda message: True, content_types=["text", "photo"])
def handler(input_text):
    if input_text.text is not None:
        user_message = input_text.text.lower()
    elif input_text.caption is not None:
        user_message = input_text.caption.lower()
    else:
        return

    if "apakah" in user_message:
        bot.reply_to(input_text, random.choice(answers))

bot.polling()