import os
import logging
import random
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- Налаштування ---
logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("TOKEN")

# Стан гри: {chat_id: {"mode": "...", "status": "...", "last_task": "..."}}
games = {}

QUESTIONS = ["Найнезручніший момент у житті?", "Твоя найбільша мрія?", "Чого ти боїшся найбільше?"]
DARES = ["Обійми людину поруч", "Зроби 5 присідань", "Розкажи секрет"]

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
    await query.answer()

    if query.data.startswith('mode_'):
        mode = query.data.split('_')[1]
        games[chat_id] = {"mode": mode, "status": "idle"}
        
        if mode == "together":
            kb = [[InlineKeyboardButton("Правда", callback_data='truth'), InlineKeyboardButton("Дія", callback_data='dare')]]
            await query.message.edit_text("Режим 'Разом'. Обирай:", reply_markup=InlineKeyboardMarkup(kb))
        else:
            await query.message.edit_text("Режим 'На відстані'. Натисни, щоб отримати питання:", 
                                          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❓ Запитати", callback_data='ask_question')]]))

    elif query.data in ['truth', 'dare']:
        task = random.choice(QUESTIONS if query.data == 'truth' else DARES)
        games[chat_id]["status"] = "waiting_for_answer"
        games[chat_id]["last_task"] = task
        await query.message.edit_text(f"Завдання: {task}\n\n👉 Напиши свою відповідь:")

    elif query.data == 'ask_question':
        task = random.choice(QUESTIONS)
        games[chat_id]["status"] = "waiting_for_answer"
        await query.message.edit_text(f"❓ Питання: {task}\n\n👉 Напиши свою відповідь:")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text
    game = games.get(chat_id)

    if game and game.get("status") == "waiting_for_answer":
        game["status"] = "idle"
        kb = [[InlineKeyboardButton("🔄 Запитати знову", callback_data='ask_question' if game["mode"] == "distance" else 'mode_together')]]
        await update.message.reply_text(f"✅ Прийнято: {text}", reply_markup=InlineKeyboardMarkup(kb))

# --- Flask для Render ---
server = Flask(__name__)
@server.route('/')
def index(): return "Бот активний!"

def run_web():
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

if __name__ == '__main__':
    Thread(target=run_web).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
