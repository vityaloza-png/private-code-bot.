import os
import logging
import random
from flask import Flask
from threading import Thread
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- Налаштування ---
logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("TOKEN")

# Стан гри: {chat_id: {"mode": "...", "status": "...", "asker_id": id}}
games = {}

QUESTIONS = ["Найнезручніший момент у житті?", "Твоя найбільша мрія?", "Чого ти боїшся найбільше?"]
DARES = ["Обійми людину поруч", "Зроби 5 присідань", "Розкажи свій секрет"]

# --- Меню ---
def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Разом (Правда/Дія)", callback_data='mode_together')],
        [InlineKeyboardButton("🌐 На відстані (Тільки Правда)", callback_data='mode_distance')]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Вітаю! Обирай режим гри:", reply_markup=get_main_menu())

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    await query.answer()

    if query.data.startswith('mode_'):
        mode = query.data.split('_')[1]
        games[chat_id] = {"mode": mode, "status": "idle", "asker_id": user_id}
        
        if mode == "together":
            kb = [[InlineKeyboardButton("Правда", callback_data='truth'), InlineKeyboardButton("Дія", callback_data='dare')]]
            await query.message.edit_text("Режим 'Разом'. Перший гравець, обирай завдання:", reply_markup=InlineKeyboardMarkup(kb))
        else:
            await query.message.edit_text("Режим 'На відстані'. Натисни кнопку, щоб отримати питання:", 
                                          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❓ Запитати", callback_data='ask_question')]]))

    elif query.data in ['truth', 'dare', 'ask_question']:
        game = games.get(chat_id)
        if not game: return
        
        game["status"] = "waiting_for_answer"
        game["asker_id"] = user_id # Оновлюємо того, хто щойно запитав
        task = random.choice(QUESTIONS) if query.data != 'dare' else random.choice(DARES)
        
        # Видаляємо кнопки, щоб відкрити поле вводу
        await query.message.edit_text(f"❓ {task}\n\n👉 *Очікуємо відповідь від іншого гравця...*", reply_markup=None)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    game = games.get(chat_id)

    if not game or game.get("status") != "waiting_for_answer":
        return

    # Сувора перевірка: чи не сам гравець собі відповідає
    if user_id == game["asker_id"]:
        await update.message.reply_text("⛔️ Ти не можеш відповідати на власне питання!")
        return

    # Відповідь прийнято
    game["status"] = "idle"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Запитати знову", callback_data='ask_question' if game["mode"] == 'distance' else 'mode_together')]])
    
    await update.message.reply_text(f"✅ Відповідь прийнято: {update.message.text}", reply_markup=kb)

# --- Flask для Render ---
server = Flask(__name__)
@server.route('/')
def index(): return "Бот активний!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    server.run(host="0.0.0.0", port=port)

# --- Запуск ---
if __name__ == '__main__':
    Thread(target=run_web).start()
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling()
