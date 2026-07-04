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

# Налаштування логів
logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("TOKEN")

games = {}
QUESTIONS = ["Найнезручніший момент?", "Твоя мрія?", "Чого ти боїшся?"]
DARES = ["Обійми сусіда", "Зроби 5 присідань", "Розкажи секрет"]

def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Разом", callback_data='mode_together')],
        [InlineKeyboardButton("🌐 На відстані", callback_data='mode_distance')]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Вітаю! Обирай режим гри:", reply_markup=get_main_menu())

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    await query.answer()
    
    if query.data == 'mode_distance':
        games[chat_id] = {"mode": "distance", "status": "waiting_for_second_player", "asker_id": None}
        await query.message.edit_text(
            "🌐 Режим 'На відстані'.\n\nГра створена! Чекаємо другого гравця.\n"
            "Другий гравець, натисни кнопку, щоб увійти в гру!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Приєднатися до гри", callback_data='join_game')]]))

    elif query.data == 'join_game':
        game = games.get(chat_id)
        if game:
            game["asker_id"] = user_id
            game["status"] = "idle"
            await query.message.edit_text(
                f"Гравець {update.effective_user.first_name} приєднався!\n"
                "Тепер можна починати:",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❓ Запитати", callback_data='ask_task')]]))

    elif query.data == 'ask_task':
        game = games.get(chat_id)
        if game:
            game["asker_id"] = user_id
            kb = [[InlineKeyboardButton("Правда", callback_data='truth'), InlineKeyboardButton("Дія", callback_data='dare')]]
            await query.message.edit_text("Обирай завдання для іншого гравця:", reply_markup=InlineKeyboardMarkup(kb))

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

    if user_id == game["asker_id"]:
        await update.message.reply_text("⛔️ Ти запитувач! Чекай, поки інший гравець напише відповідь.")
        return

    game["status"] = "idle"
    game["asker_id"] = user_id 
    
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Наступне запитання", callback_data='ask_task')]])
    await update.message.reply_text(f"✅ Відповідь прийнято: {update.message.text}\n\nТепер черга {update.effective_user.first_name} задавати питання!", reply_markup=kb)

# --- ОСНОВНИЙ ЗАПУСК (ось це критично важливо!) ---
if __name__ == '__main__':
    if not TOKEN:
        print("ПОМИЛКА: Не знайдено TOKEN у змінних середовища!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_callback))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("Бот запущений!")
        app.run_polling()
