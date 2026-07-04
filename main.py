import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- НАЛАШТУВАННЯ ---
TOKEN = "8671245475:AAFEslZmW0ih6hYQm0wupTd3SVqoyzdvFm8"

# --- ПИТАННЯ ТА ДІЇ (Список тут) ---
truths = [
    "Яка твоя найтаємніша мрія?", "Який твій найбільший страх?", 
    "Що ти першим ділом помітила в мені?", "Яка твоя найбільша таємниця?"
]
dares = [
    "Зроби 20 присідань", "Напиши мені комплімент", 
    "Затанцюй під першу-ліпшу пісню", "Зроби мені масаж 5 хвилин"
]

# --- ГЛОБАЛЬНІ ЗМІННІ (Кеш) ---
waiting_player = None
players_map = {}

# --- ФУНКЦІЇ БОТА ---
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
        # Очищення пам'яті (кешу)
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

    if "far" in query.data:
        text = f"Питання: {random.choice(truths)}"
        await context.bot.send_message(chat_id=partner_id, text=text)
        await query.edit_message_text("Питання успішно відправлено партнеру!")
    else:
        text = f"Завдання для вас двох:\n\n{random.choice(truths + dares)}"
        await query.edit_message_text(text)

# --- ЗАПУСК ---
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Бот запущений...")
    app.run_polling()
