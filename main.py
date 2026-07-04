import sys
import os
sys.path.append(os.getcwd())

from questions import truths, dares

import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from questions import truths, dares

# Глобальні змінні для зберігання пари
waiting_player = None
players_map = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global waiting_player, players_map
    user_id = update.effective_user.id
    
    if user_id in players_map:
        await update.message.reply_text("Ви вже в грі! Щоб зупинити, натисніть /stop")
        return

    if waiting_player is None:
        waiting_player = user_id
        await update.message.reply_text("Чекаю на другого гравця...")
    else:
        partner_id = waiting_player
        players_map[user_id] = partner_id
        players_map[partner_id] = user_id
        waiting_player = None 
        
        keyboard = [
            [InlineKeyboardButton("На відстані (Тільки питання)", callback_data="far_truth")],
            [InlineKeyboardButton("Поряд (Питання + Дії)", callback_data="near_all")]
        ]
        msg = "Партнер знайшовся! Оберіть формат гри:"
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
        await context.bot.send_message(chat_id=partner_id, text=msg, reply_markup=InlineKeyboardMarkup(keyboard))

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global waiting_player, players_map
    user_id = update.effective_user.id
    
    if user_id in players_map:
        partner_id = players_map[user_id]
        del players_map[user_id]
        del players_map[partner_id]
        await update.message.reply_text("Гру зупинено. Кеш очищено.")
        await context.bot.send_message(chat_id=partner_id, text="Партнер зупинив гру. Кеш очищено.")
    elif waiting_player == user_id:
        waiting_player = None
        await update.message.reply_text("Пошук партнера скасовано.")
    else:
        await update.message.reply_text("Ви зараз не в грі.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    sender_id = update.effective_user.id
    partner_id = players_map.get(sender_id)
    
    if not partner_id:
        await query.edit_message_text("Помилка: партнер не знайдений. Натисніть /start")
        return

    mode = query.data
    if "far" in mode:
        text = f"Питання: {random.choice(truths)}"
        await context.bot.send_message(chat_id=partner_id, text=text)
        await query.edit_message_text("Питання успішно відправлено партнеру!")
    else:
        text = f"Завдання для вас двох:\n\n{random.choice(truths + dares)}"
        await query.edit_message_text(text)

app = Application.builder().token("ТВІЙ_ТОКЕН").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stop", stop))
app.add_handler(CallbackQueryHandler(button_handler))
app.run_polling()
