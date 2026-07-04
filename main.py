import os
import logging
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    CallbackQueryHandler, 
    MessageHandler, 
    filters, 
    ContextTypes
)

# Налаштування
logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("TOKEN")

# Словник для зберігання стану гри
games = {}

QUESTIONS = ["Найнезручніший момент?", "Твоя мрія?", "Чого ти боїшся?"]
DARES = ["Обійми сусіда", "Зроби 5 присідань", "Розкажи секрет"]

# --- Меню ---
def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Разом", callback_data='mode_together')],
        [InlineKeyboardButton("🌐 На відстані", callback_data='mode_distance')]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Вітаю! Обирай режим гри (найкраще працює в групі):", reply_markup=get_main_menu())

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    await query.answer()
    
    # 1. Створення гри
    if query.data == 'mode_distance':
        games[chat_id] = {
            "status": "waiting_for_second_player", 
            "asker_id": None, 
            "player1_id": user_id, 
            "player2_id": None
        }
        await query.message.edit_text(
            "🌐 Режим 'На відстані'.\n\nГра створена! Другий гравець, приєднайся:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Приєднатися", callback_data='join_game')]])
        )

    # 2. Приєднання
    elif query.data == 'join_game':
        game = games.get(chat_id)
        if game and game["status"] == "waiting_for_second_player":
            game["player2_id"] = user_id
            game["status"] = "idle"
            await query.message.edit_text(
                f"✅ {update.effective_user.first_name} приєднався!\nТепер можна грати.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❓ Запитати", callback_data='ask_task')]])
            )

    # 3. Вибір завдання
    elif query.data == 'ask_task':
        game = games.get(chat_id)
        if game:
            game["asker_id"] = user_id
            kb = [[InlineKeyboardButton("Правда", callback_data='truth'), InlineKeyboardButton("Дія", callback_data='dare')]]
            await query.message.edit_text("Обирай завдання для іншого гравця:", reply_markup=InlineKeyboardMarkup(kb))

    # 4. Виконання
    elif query.data in ['truth', 'dare']:
        game = games.get(chat_id)
        if game:
            game["status"] = "waiting_for_answer"
            task = random.choice(QUESTIONS if query.data == 'truth' else DARES)
            await query.message.edit_text(f"❓ {task}\n\n👉 *Чекаємо відповідь від іншого гравця...*")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    game = games.get(chat_id)

    if not game or game.get("status") != "waiting_for_answer":
        return

    # Перевірка, щоб відповідав не той, хто запитав
    if user_id == game["asker_id"]:
        return

    game["status"] = "idle"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Наступне запитання", callback_data='ask_task')]])
    await update.message.reply_text(
        f"✅ Відповідь: {update.message.text}\n\nЧерга {update.effective_user.first_name} запитувати!", 
        reply_markup=kb
    )

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
