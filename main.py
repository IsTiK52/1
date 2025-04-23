
import os
import telebot
import json
import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

SCHEDULE_PATH = "words_schedule.json"
PROGRESS_PATH = "storage/progress.csv"
REPETITION_PATH = "storage/repetition.json"

with open(SCHEDULE_PATH, encoding="utf-8") as f:
    schedule = json.load(f)

def get_today_words():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    return schedule.get(today)

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я VocabularBot. Нажми 📘 Слова дня")

@bot.message_handler(commands=["menu"])
def menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📘 Слова дня", "🔁 Повторение", "📊 Прогресс")
    bot.send_message(message.chat.id, "Выбери действие:", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_menu(message):
    if message.text == "📘 Слова дня":
        data = get_today_words()
        if not data:
            bot.send_message(message.chat.id, "На сегодня слов нет.")
            return

        theme = data["theme"]
        text = f"🎯 Тема: {theme}\n\n"
        for w in data["words"]:
            text += f"🔹 *{w['word']}* ({w['pos']}) — {w['translation']}\n_{w['example']}_\n\n"

        with open(PROGRESS_PATH, "a", encoding="utf-8") as f:
            f.write(f"{message.from_user.id},{datetime.datetime.now().strftime('%Y-%m-%d')},{theme}\n")

        bot.send_message(message.chat.id, text, parse_mode="Markdown")
    elif message.text == "🔁 Повторение":
        with open(REPETITION_PATH, encoding="utf-8") as f:
            rep = json.load(f)
        words = rep.get(str(message.from_user.id), [])
        text = "\n".join(f"🔁 {w}" for w in words) or "Нет слов для повторения."
        bot.send_message(message.chat.id, text)
    elif message.text == "📊 Прогресс":
        with open(PROGRESS_PATH, encoding="utf-8") as f:
            lines = [line.strip().split(",") for line in f.readlines()]
        user_themes = [line[2] for line in lines if line[0] == str(message.from_user.id)]
        msg = "\n".join(f"✅ {theme}" for theme in user_themes) if user_themes else "Нет пройденных тем."
        bot.send_message(message.chat.id, msg)

bot.polling()
