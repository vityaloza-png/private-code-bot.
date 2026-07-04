import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- НАЛАШТУВАННЯ ---
TOKEN = "8671245475:AAFEslZmW0ih6hYQm0wupTd3SVqoyzdvFm8"

truths = ["Яка твоя найтаємніша мрія?", "Який твій найбільший страх?", "Що ти першим ділом помітила в мені?", "Що б ти зробила, якби ми залишилися одні?"]
dares = ["Зроби 20 присідань", "Напиши мені комплімент", "Затанцюй", "Зроби мені масаж 5 хвилин"]

waiting_player = None
players_map = {}

# --- ФУНКЦІЇ ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global waiting_player, players_map
    user_id = update.effective_user.id
    
    if user_id in players_map:
        await update.message.reply_text("🔥 Ти вже в грі. Не відволікайся!")
        return

    if waiting_player is None:
        waiting_player = user_id
        await update.message.reply_text("❤️ Пошук розпочато... Чекаю на того, хто готовий зіграти.")
    else:
        partner_id = waiting_player
        players_map[user_id] = partner_id
        players_map[partner_id] = user_id
        waiting_player = None 
        
        keyboard = [
            [InlineKeyboardButton("Тільки питання", callback_data="far_truth")],
            [InlineKeyboardButton("Питання та Дії", callback_data="near_all")]
        ]
        msg = "🔥 Знайдено. Готуйся, гра стає цікавішою. Обирай формат:"
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
        await context.bot.send_message(chat_id=partner_id, text=msg, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    sender_id = update.effective_user.id
    partner_id = players_map.get(sender_id)
    
    if not partner_id:
        await query.edit_message_text("❌ Помилка: партнер не знайдений.")
        return

    task = random.choice(truths + dares)
    scale_keyboard = [
        [InlineKeyboardButton("1", callback_data="level_1"), 
         InlineKeyboardButton("2", callback_data="level_2"),
         InlineKeyboardButton("3", callback_data="level_3"),
         InlineKeyboardButton("4", callback_data="level_4"),
         InlineKeyboardButton("5🔥", callback_data="level_5")]
    ]
    
    msg = f"🔥 Питання/Дія: {task}\n\nОціни рівень своєї реакції (1-5):"
    
    await context.bot.send_message(chat_id=sender_id, text=msg, reply_markup=InlineKeyboardMarkup(scale_keyboard))
    await context.bot.send_message(chat_id=partner_id, text=f"👀 Зараз відповідає твій партнер:\n{task}")
    await query.edit_message_text("✅ Завдання відправлено. Чекаємо на відповідь.")

async def scale_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    level = query.data.split("_")[1]
    sender_id = update.effective_user.id
    partner_id = players_map.get(sender_id)
    
    await query.edit_message_text(f"🔥 Твій рівень збудження: {level}/5")
    if partner_id:
        await context.bot.send_message(chat_id=partner_id, text=f"🌡 Рівень реакції партнера: {level}/5")

# --- ЗАПУСК ---
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(far|near)"))
    app.add_handler(CallbackQueryHandler(scale_handler, pattern="^level_"))
    print("Бот запущений...")
    app.run_polling()
