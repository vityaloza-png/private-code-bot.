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

       а # Глобальні змінні
    waiting_players = []  
       # Список тих, хто чекає на гру
     games = {}            # Активні ігри

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    await query.answer()

    if query.data == 'join_game':
        # Якщо гравець вже в черзі — ігноруємо
        if user.id in waiting_players:
            await query.edit_message_text("Ви вже в черзі, чекаємо іншого гравця...")
            return

        waiting_players.append(user.id)
        await query.edit_message_text("Ви в черзі! Чекаємо на суперника...")

    # Якщо в черзі двоє — з'єднуємо їх
    if len(waiting_players) >= 2:
            player1 = waiting_players.pop(0)
            player2 = waiting_players.pop(0)
            
            # Створюємо гру для цих двох ID
            game_id = f"game_{player1}_{player2}"
            games[game_id] = {"players": [player1, player2]}
            
            # Повідомляємо обох
            await context.bot.send_message(player1, "Знайдено суперника! Гра починається.")
            await context.bot.send_message(player2, "Знайдено суперника! Гра починається.")

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
    
# Основний блок запуску
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("Бот запускається...")
    app.run_polling()