import os
import logging
from flask import Flask
from threading import Thread
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Словник для зберігання гравців сесії: {chat_id: {"players": [], "asker_id": None, "status": "..."}}
games = {}

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    await query.answer()

# --- Налаштування ---
logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("TOKEN")

    # 1. Початок гри (Створення сесії)
    if query.data == 'start_game':
        games[chat_id] = {"players": [user_id], "status": "waiting_for_second"}
        await query.message.edit_text("Сесію створено! Чекаємо другого гравця.\nДругий гравець, натисни кнопку нижче!", 
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Приєднатися", callback_data='join_game')]]))

# 2. Другий гравець приєднується
    elif query.data == 'join_game':
        game = games.get(chat_id)
        if not game: return
        
        if user_id in game["players"]:
            await query.answer("Ти вже в грі!")
            return
            
        game["players"].append(user_id)
        game["status"] = "idle"
        await query.message.edit_text("Гру    розпочато! Обидва гравці в мережі.", 

# --- Меню та функції ---
main_menu = ReplyKeyboardMarkup([
    ['🔥 Разом (Правда/Дія)', '🌐 На відстані (Тільки Правда)'],
    ['🔄 Перезапустити гру']
], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Вітаю! Обирай режим гри нижче:", reply_markup=main_menu)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == '🌐 На відстані (Тільки Правда)':
        keyboard = [[InlineKeyboardButton(str(i), callback_data=f'rate_{i}') for i in range(1, 6)]]
        await update.message.reply_text("🔥 Завдання: Твоя найтаємніша мрія?\n\nОціни реакцію:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif text == '🔥 Разом (Правда/Дія)':
        keyboard = [[InlineKeyboardButton("Правда", callback_data='truth'), InlineKeyboardButton("Дія", callback_data='dare')]]
        await update.message.reply_text("Обирай:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif text == '🔄 Перезапустити гру':
        await update.message.reply_text("Гру перезапущено! Обирай режим:", reply_markup=main_menu)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith('rate_'):
        await query.message.reply_text(f"🌡 Рівень збудження: {query.data.split('_')[1]}/5")
    elif query.data == 'truth':
        await query.message.reply_text("Твоя правда: Розкажи про свій найнезручніший момент у житті.")
    elif query.data == 'dare':
        await query.message.reply_text("Твоя дія: Обійми людину, яка сидить найближче до тебе.")

# --- Flask-заглушка для Render ---
server = Flask(__name__)
@server.route('/')
def index():
    return "Бот активний!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    server.run(host="0.0.0.0", port=port)

# --- Запуск ---
if __name__ == '__main__':
    # Запуск веб-сервера в окремому потоці
    Thread(target=run_web).start()
    
    # Запуск бота
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))
    
