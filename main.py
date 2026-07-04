import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "8671245475:AAFEslZmW0ih6hYQm0wupTd3SVqoyzdvFm8"

# Твої списки
truths = ["Твоя найтаємніша мрія?", "Найбільший страх?", "Що першим помітила в мені?"]
dares = ["Зроби 20 присідань", "Напиши комплімент", "Зроби масаж 5 хв"]

# --- КЛАВІАТУРА (Завжди внизу) ---
def get_main_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🔥 Разом (Правда/Дія)"), KeyboardButton("🌐 На відстані (Тільки Правда)")],
        [KeyboardButton("🔄 Перезапустити гру")]
    ], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Вітаю! Обирай режим гри нижче:", reply_markup=get_main_menu())

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "🔥 Разом (Правда/Дія)":
        await update.message.reply_text("Обирай:", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Правда", callback_data="type_truth"), InlineKeyboardButton("Дія", callback_data="type_dare")]
        ]))
    elif text == "🌐 На відстані (Тільки Правда)":
        task = random.choice(truths)
        await send_task_with_scale(update, task)
    elif text == "🔄 Перезапустити гру":
        await start(update, context)

async def send_task_with_scale(update, task):
    scale_keyboard = [[InlineKeyboardButton(str(i), callback_data=f"level_{i}") for i in range(1, 6)]]
    await update.message.reply_text(f"🔥 Завдання:\n{task}\n\nОціни реакцію:", reply_markup=InlineKeyboardMarkup(scale_keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if "type_" in data:
        task = random.choice(truths if "truth" in data else dares)
        await send_task_with_scale(query.message, task)
    elif "level_" in data:
        level = data.split("_")[1]
        await query.edit_message_text(f"🌡 Рівень збудження: {level}/5")

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Бот запущений...")
    app.run_polling()
