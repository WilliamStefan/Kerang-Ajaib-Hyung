import os
import random
import telebot
import logging
from dotenv import load_dotenv

load_dotenv()

# logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

answers = ["Ya", "Nggak"] # Jawaban si bot Kerang Ajaib Hyung

# Token si bot Kerang Ajaib Hyung
bot = telebot.TeleBot(os.environ['API_KEY'])

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
