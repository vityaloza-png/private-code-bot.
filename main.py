import os
import logging
import random
from flask import Flask
from threading import Thread
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("TOKEN")

# Стан: {chat_id: {"mode": "...", "asker_id": id, "status": "..."}}
games = {}

QUESTIONS = ["Найнезручніший момент?", "Твоя мрія?", "Чого ти боїшся?"]
DARES = ["Обійми сусіда", "Зроби 5 присідань", "Розкажи секрет"]

# --- Меню ---
def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Разом (Правда/Дія)", callback_data='mode_together')],
        [InlineKeyboardButton("🌐 На відстані", callback_data='mode_distance')]
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
        games[chat_id] = {"mode": mode, "asker_id": user_id, "status": "idle"}
        await query.message.edit_text(f"Режим '{mode}'. Чекаю на вибір завдання...", 
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❓ Запитати", callback_data='ask_task')]]))

    elif query.data == 'ask_task':
        # Тепер той, хто натиснув кнопку - запитувач
        games[chat_id]["asker_id"] = user_id
        kb = [[InlineKeyboardButton("Правда", callback_data='truth'), InlineKeyboardButton("Дія", callback_data='dare')]]
        await query.message.edit_text("Обирай завдання для іншого гравця:", reply_markup=InlineKeyboardMarkup(kb))

    elif query.data in ['truth', 'dare']:
        games[chat_id]["status"] = "waiting_for_answer"
        task = random.choice(QUESTIONS if query.data == 'truth' else DARES)
        await query.message.edit_text(f"❓ {task}\n\n👉 *Чекаємо відповідь від іншого гравця...*", reply_markup=None)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    game = games.get(chat_id)

    if not game or game.get("status") != "waiting_for_answer":
        return

    if user_id == game["asker_id"]:
        await update.message.reply_text("⛔️ Ти запитувач! Чекай, поки інший гравець напише відповідь.")
        return

    # Відповідь отримана
    game["status"] = "idle"
    # Міняємо ролі: тепер той, хто відповідав, стає головним для вибору наступного кроку
    game["asker_id"] = user_id 
    
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Наступне запитання", callback_data='ask_task')]])
    await update.message.reply_text(f"✅ Відповідь прийнято: {update.message.text}\n\nТепер черга {update.effective_user.first_name} задавати питання!", reply_markup=kb)

# --- Flask та Запуск (як раніше) ---
