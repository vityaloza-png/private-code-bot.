import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Словник для зберігання гравців сесії: {chat_id: {"players": [], "asker_id": None, "status": "..."}}
games = {}

# --- Глобальні змінні (початок файлу, без відступів) ---
logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("TOKEN")
games = {}

# Список, де будуть зберігатися ID гравців, що чекають
waiting_players = []

async def start(update, context):
    keyboard = [[InlineKeyboardButton("✅ Приєднатися", callback_data='join_game')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Натисни кнопку, щоб знайти суперника:", reply_markup=reply_markup)

async def button_callback(update, context):
    query = update.callback_query
    user = update.effective_user
    await query.answer()

    if query.data == 'join_game':
        # Перевірка: чи не стоїть гравець вже в черзі
        if user.id in waiting_players:
            await query.edit_message_text("Ви вже в черзі, чекаємо іншого гравця...")
            return

        waiting_players.append(user.id)
        await query.edit_message_text(f"Гравець {user.first_name} в черзі! Чекаємо на другого...")

        # Якщо в черзі двоє — з'єднуємо їх
    if len(waiting_players) >= 2:
            player1 = waiting_players.pop(0)
            player2 = waiting_players.pop(0)
            
            # Повідомляємо обох про початок гри
            await context.bot.send_message(player1, "Знайдено суперника! Гра починається.")
            await context.bot.send_message(player2, "Знайдено суперника! Гра починається.")
    
# Основний блок запуску
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("Бот запускається...")
    app.run_polling()