import os
import threading
import logging
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# 1. Налаштування логів
logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("TOKEN")

# Список тих, хто чекає на гру
waiting_players = []

# 2. Логіка Flask (обманка для Render)
app = Flask(__name__)

@app.route('/health')
def health():
    return "OK", 200

@app.route('/')
def home():
    return "Бот активний!", 200

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# 3. Логіка бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("✅ Приєднатися", callback_data='join_game')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Натисни кнопку, щоб знайти суперника:", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    await query.answer()

    if query.data == 'join_game':
        if user.id in waiting_players:
            await query.edit_message_text("Ви вже в черзі...")
            return

        waiting_players.append(user.id)
        await query.edit_message_text(f"Гравець {user.first_name} в черзі! Чекаємо другого...")

        if len(waiting_players) >= 2:
            player1 = waiting_players.pop(0)
            player2 = waiting_players.pop(0)
            await context.bot.send_message(player1, "Знайдено суперника! Гра починається.")
            await context.bot.send_message(player2, "Знайдено суперника! Гра починається.")

# 4. Запуск
if __name__ == '__main__':
    # Запуск Flask в окремому потоці
    threading.Thread(target=run_web, daemon=True).start()
    
    # Запуск бота
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CallbackQueryHandler(button_callback))
    
    print("Бот запущено!")
    bot_app.run_polling()
