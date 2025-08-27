import logging
from aiogram import Bot, Dispatcher, executor, types
import wikipedia
import json
import os

# === Настройки ===
TOKEN = "8358041339:AAGfYWu9Qve-2NtBaNIPFY1ExA973ruo4pI"   # твой токен бота
ADMIN_ID = 6454793905                                      # твой Telegram ID
wikipedia.set_lang("ru")

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# === Работа с базой знаний ===
FILE = "knowledge.json"

def load_knowledge():
    if os.path.exists(FILE):
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "математика": {
            "пифагор": "Теорема Пифагора: a² + b² = c²",
            "квадратное уравнение": "Решение: x = (-b ± √(b²-4ac)) / 2a"
        },
        "физика": {
            "сила": "F = m * a (второй закон Ньютона)",
            "работа": "A = F * s * cos(α)"
        },
        "химия": {
            "вода": "H₂O — оксид водорода",
            "углекислый газ": "CO₂ — углекислый газ"
        },
        "биология": {
            "митоз": "Митоз — процесс деления клетки на две дочерние клетки",
            "фотосинтез": "Фотосинтез — процесс образования органических веществ из CO₂ и H₂O при свете"
        },
        "русский язык": {
            "главные члены предложения": "Подлежащее и сказуемое",
            "виды глаголов": "Совершенный и несовершенный"
        }
    }

def save_knowledge():
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(knowledge_base, f, indent=4, ensure_ascii=False)

knowledge_base = load_knowledge()

def find_answer(subject, query):
    subject = subject.lower()
    query = query.lower()
    if subject in knowledge_base:
        for key, answer in knowledge_base[subject].items():
            if key in query:
                return answer
    try:
        result = wikipedia.summary(query, sentences=2)
        return result
    except Exception as e:
        logging.error(f"Wiki error: {e}")
        return "Извини, я не нашёл ответ 😢"

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        "Привет 👋 Я школьный бот-помощник!\n\n"
        "Напиши вопрос в формате:\n"
        "📘 предмет: вопрос\n\n"
        "Примеры:\n"
        "математика: теорема пифагора\n"
        "физика: работа силы\n\n"
        "🔑 Только админ может добавлять новые ответы:\n"
        "/add предмет|ключевое слово|ответ",
        parse_mode="Markdown"
    )

@dp.message_handler(commands=['add'])
async def add_knowledge(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ У тебя нет прав для добавления информации.")
        return
    try:
        _, data = message.text.split(" ", 1)
        subject, keyword, answer = data.split("|")
        subject = subject.strip().lower()
        keyword = keyword.strip().lower()
        answer = answer.strip()
        if subject not in knowledge_base:
            knowledge_base[subject] = {}
        knowledge_base[subject][keyword] = answer
        save_knowledge()
        await message.answer(
            f"✅ Добавлено в базу:\n\n📘 *{subject}*\n🔑 {keyword}\n💡 {answer}",
            parse_mode="Markdown"
        )
    except:
        await message.answer("❌ Ошибка формата. Используй:\n/add предмет|ключевое слово|ответ", parse_mode="Markdown")

@dp.message_handler()
async def answer(message: types.Message):
    if ":" not in message.text:
        await message.answer(
            "Пожалуйста, укажи предмет и вопрос через :.\n"
            "Например: химия: вода",
            parse_mode="Markdown"
        )
        return
    subject, query = message.text.split(":", 1)
    subject, query = subject.strip(), query.strip()
    response = find_answer(subject, query)
    await message.answer(response)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
