import os
import random
import telebot
import logging
import traceback
from dotenv import load_dotenv
import openai
import re
from chat_history import append_history, get_history


load_dotenv()


def log(message: str):
    print(message, flush=True)


# logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

whitelisted_groups = [int(a) for a in os.environ["WHITELISTED_CHAT_IDS"].split(",")]

answers = ["Ya", "Nggak"]  # Jawaban si bot Kerang Ajaib Hyung

# Token si bot Kerang Ajaib Hyung
bot = telebot.TeleBot(os.environ["API_KEY"])

bot_details = bot.get_me()
bot_username = bot_details.username
bot_id = bot_details.id


# Set OpenAI API key
openai.api_key = os.environ["OPENAI_API_KEY"]

OPENAI_MODEL = "gpt-4"
OPENAI_SYSTEM_MESSAGE = "\n".join(
    [
        "You are Kerang Ajaib, a bot that knows everything and always try to be witty with the response.",
        "You will answer as clever as possible, sarcastic at times, but also prefer brief answers.",
        "You prefer to reply in Bahasa Indonesia, but of course you are fluent in other languages as well.",
    ]
)


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

    log(f"[{group_id}] {user}: {user_message}")

    reply_to = None
    if message.reply_to_message is not None:
        if message.reply_to_message.from_user.id == bot_id:
            reply_to = "Kerang Ajaib: " + message.reply_to_message.text
        else:
            reply_to = message.reply_to_message.from_user.first_name
            if message.reply_to_message.from_user.last_name:
                reply_to += " " + message.reply_to_message.from_user.last_name
            reply_to += ": " + message.reply_to_message.text

    append_history(group_id, user, user_message, reply_to)

    # Don't reply to bot
    if message.from_user.is_bot:
        return

    def respond_randomly():
        answer = random.choice(answers)
        bot.reply_to(message, answer)
        append_history(group_id, "Kerang Ajaib", answer, f"{user}: {user_message}")

    def respond_with_chatgpt():
        try:
            messages = [
                {
                    "role": "system",
                    "content": OPENAI_SYSTEM_MESSAGE,
                }
            ]

            # Compose messages from last 10 chats
            history = get_history(group_id)
            for chat in history:
                if chat.user == "Kerang Ajaib":
                    msg = chat.message
                    if chat.reply_to is not None:
                        msg += "\n---\nReplying to:\n" + chat.reply_to
                    messages.append({"role": "assistant", "content": msg})
                else:
                    msg = f"{chat.user}: {chat.message}"
                    if chat.reply_to is not None:
                        msg += "\n---\nReplying to:\n" + chat.reply_to
                    messages.append({"role": "user", "content": msg})

            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                log(f"[{group_id}][OPENAI][CONTEXT]: [{role}] {content}")

            chat_completion = openai.ChatCompletion.create(model=OPENAI_MODEL, messages=messages)

            answer = chat_completion.choices[0].message.content

            log(f"[{group_id}][OPENAI][ANSWER] : {answer}")

            # Trim --- Replying to: if it exists
            reply_to_regex = r"\s*-{3,}\s+Reply(ing)? to\s*:?\s*"
            if re.search(reply_to_regex, answer):
                answer = re.split(reply_to_regex, answer)[0]
                answer = answer.strip()

            bot.reply_to(message, answer)

            append_history(group_id, "Kerang Ajaib", answer, f"{user}: {user_message}")

        except Exception as e:
            log(f"Error calling OpenAI API: {repr(e)}")
            traceback.print_exc()

    if "apakah" in user_message.lower():
        respond_randomly()
    elif "mengapa" in user_message.lower():
        respond_with_chatgpt()
    elif f"@{bot_username}" in user_message.lower():
        # Mentioning the bot will also get ChatGPT response
        respond_with_chatgpt()
    elif message.reply_to_message is not None and message.reply_to_message.from_user.id == bot_id:
        # Replies to the bot will also get ChatGPT response
        respond_with_chatgpt()


bot.polling()
