 from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- Меню знизу, як на скриншоті image_2.png ---
main_menu = ReplyKeyboardMarkup([
    ['🔥 Разом (Правда/Дія)', '🌐 На відстані (Тільки Правда)'],
    ['🔄 Перезапустити гру']
], resize_keyboard=True)

# --- Функція запуску ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Вітаю! Обирай режим гри нижче:", reply_markup=main_menu)

# --- Обробка кнопок меню ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # Режим "На відстані"
    if text == '🌐 На відстані (Тільки Правда)':
        keyboard = [[InlineKeyboardButton(str(i), callback_data=f'rate_{i}') for i in range(1, 6)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🔥 Завдання: Твоя найтаємніша мрія?\n\nОціни реакцію:", reply_markup=reply_markup)

    # Режим "Разом"
    elif text == '🔥 Разом (Правда/Дія)':
        keyboard = [[InlineKeyboardButton("Правда", callback_data='truth'), 
                     InlineKeyboardButton("Дія", callback_data='dare')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Обирай:", reply_markup=reply_markup)

# --- Обробка натискань на кнопки ---
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Реакція на оцінку збудження
    if query.data.startswith('rate_'):
        level = query.data.split('_')[1]
        await query.message.reply_text(f"🌡 Рівень збудження: {level}/5")

if __name__ == '__main__':
    # 8671245475:AAFEslZmW0ih6hYQm0wupTd3SVqoyzdvFm8Вставте сюди свій токен
    app = ApplicationBuilder().token("ВАШ_ТОКЕН_БОТА").build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("Бот запущений...")
    app.run_polling()
