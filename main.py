import os
import telebot
import json
import datetime

# Загрузка токена из переменных среды
BOT_TOKEN = os.environ.get("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

# Пути к файлам
SCHEDULE_PATH = "words_schedule.json"
PROGRESS_PATH = "progress.csv"
REPETITION_PATH = "repetition.json"

# Загрузка расписания
with open(SCHEDULE_PATH, encoding="utf-8") as f:
    schedule = json.load(f)

# Получение слов на сегодня
def get_today_words():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    return schedule.get(today)

# Команда /start
from telebot import types

@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📘 Слова дня", "🔁 Повторение")
    markup.add("📊 Мой прогресс")
    bot.send_message(message.chat.id, "Привет! Я VocabularBot. Нажми кнопку 📘 Слова дня.", reply_markup=markup)

# Главное меню
@bot.message_handler(func=lambda m: True)
def menu(message):
    if message.text == "📘 Слова дня":
        data = get_today_words()
        if not data:
            bot.send_message(message.chat.id, "На сегодня слов нет.")
            return
        theme = data["theme"]
        text = f"🎯 Тема: {theme}\n\n"
        for w in data["words"]:
            text += f"🔹 *{w['word']}* ({w['pos']}) — {w['translation']}\n_{w['example']}_\n\n"
        bot.send_message(message.chat.id, text, parse_mode="Markdown")
    elif message.text == "🔁 Повторение":
        with open(REPETITION_PATH, encoding="utf-8") as f:
            rep = json.load(f)
        words = rep.get(str(message.from_user.id), [])
        text = "\n".join(f"🔁 {w}" for w in words) if words else "Нет слов для повторения."
        bot.send_message(message.chat.id, text)
    elif message.text == "📊 Мой прогресс":
        with open(PROGRESS_PATH, encoding="utf-8") as f:
            lines = f.readlines()[1:]
        dates = {line.split(",")[1] for line in lines if str(message.from_user.id) in line}
        bot.send_message(message.chat.id, f"📈 Пройдено дней: {len(dates)}")

bot.polling()
