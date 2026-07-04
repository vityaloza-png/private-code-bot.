 import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Налаштування логування
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- Меню ---
main_menu = ReplyKeyboardMarkup([
    ['🔥 Разом (Правда/Дія)', '🌐 На відстані (Тільки Правда)'],
    ['🔄 Перезапустити гру']
], resize_keyboard=True)

# --- Функції бота ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Вітаю! Обирай режим гри нижче:", reply_markup=main_menu)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == '🌐 На відстані (Тільки Правда)':
        keyboard = [[InlineKeyboardButton(str(i), callback_data=f'rate_{i}') for i in range(1, 6)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🔥 Завдання: Твоя найтаємніша мрія?\n\nОціни реакцію:", reply_markup=reply_markup)

    elif text == '🔥 Разом (Правда/Дія)':
        keyboard = [[InlineKeyboardButton("Правда", callback_data='truth'), 
                     InlineKeyboardButton("Дія", callback_data='dare')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Обирай:", reply_markup=reply_markup)
    
    elif text == '🔄 Перезапустити гру':
        await update.message.reply_text("Гру перезапущено! Обирай режим:", reply_markup=main_menu)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith('rate_'):
        level = query.data.split('_')[1]
        await query.message.reply_text(f"🌡 Рівень збудження: {level}/5")
    elif query.data == 'truth':
        await query.message.reply_text("Твоя правда: Розкажи про свій найнезручніший момент у житті.")
    elif query.data == 'dare':
        await query.message.reply_text("Твоя дія: Обійми людину, яка сидить найближче до тебе.")

if __name__ == '__main__':
    # Токен вставлено напряму
    TOKEN = "8857921196:AAFeu3bG_Sr9050coijFk7yjrZdmu6I0INE"
    
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("Бот успішно запущений...")
    app.run_polling()
