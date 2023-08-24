import os
import random
import telebot
import logging
from typing import Any
from dotenv import load_dotenv

load_dotenv()

import openai

# logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

whitelisted_groups = [int(a) for a in os.environ['WHITELISTED_CHAT_IDS'].split(",")]

answers = ["Ya", "Nggak"] # Jawaban si bot Kerang Ajaib Hyung

# Token si bot Kerang Ajaib Hyung
bot = telebot.TeleBot(os.environ['API_KEY'])

history = {}

def append_history(group_id: Any, user: str, message: str):
    gid = group_id
    if gid not in history:
        history[gid] = [{
            "user": user,
            "message": message,
        }]
    else:
        history[gid].append({
            "user": user,
            "message": message,
        })
    # Only keep last 10 items
    history[gid] = history[gid][-10:]

bot_id = bot.get_me().id

@bot.message_handler(func=lambda message: True, content_types=["text", "photo"])
def handler(message: telebot.types.Message):
    # Only respond to whitelisted groups
    group_id = message.chat.id
    if group_id not in whitelisted_groups:
        return

    if message.text is not None:
        user_message = message.text
    elif message.caption is not None:
        user_message = message.caption
    else:
        return

    user = message.from_user.first_name
    if message.from_user.last_name:
        user += " " + message.from_user.last_name

    print(f"[{group_id}] {user}: {user_message}", flush=True)
    append_history(group_id, user, user_message)

    # Don't reply to bot
    if message.from_user.is_bot:
        return

    def respond_randomly():
        answer = random.choice(answers)
        bot.reply_to(message, answer)
        append_history(group_id, "Kerang Ajaib", answer)

    def respond_with_chatgpt():
        try:
            messages = [
                {"role": "system", "content": "You are Kerang Ajaib, a bot that knows everything and always try to be witty with the response. You don't have to start your message with 'Kerang Ajaib:' every time."}
            ]
            for chat in history.get(group_id, []):
                if chat["user"] == "Kerang Ajaib":
                    messages.append({"role": "assistant", "content": chat["user"] + ": " + chat["message"]})
                else:
                    messages.append({"role": "user", "content": chat["user"] + ": " + chat["message"]})

            chat_completion = openai.ChatCompletion.create(model="gpt-4", messages=messages)

            # print the chat completion
            answer = chat_completion.choices[0].message.content
            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                print(f"[{group_id}][OPENAI][CONTEXT]: [{role}] {content}", flush=True)
            print(f"[{group_id}][OPENAI][ANSWER] : {answer}", flush=True)
            bot.reply_to(message, answer)

            append_history(group_id, "Kerang Ajaib", answer)

        except Exception as e:
            print(f"Error calling OpenAI API: {e}", flush=True)

    if "apakah" in user_message.lower():
        respond_randomly()
    elif "mengapa" in user_message.lower():
        respond_with_chatgpt()
    elif message.reply_to_message is not None and message.reply_to_message.from_user.id == bot_id:
        # Replies to the bot will also get ChatGPT response
        respond_with_chatgpt()

bot.polling()
