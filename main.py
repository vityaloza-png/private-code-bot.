 import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8671245475:AAFEslZmW0ih6hYQm0wupTd3SVqoyzdvFm8"

truths = ["Яка твоя найтаємніша мрія?", "Який твій найбільший страх?", "Що ти першим ділом помітила в мені?"]
dares = ["Зроби 20 присідань", "Напиши мені комплімент", "Зроби мені масаж 5 хвилин"]

players_map = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # Спрощена логіка для тесту (підключення партнера за ID)
    await update.message.reply_text("🔥 Гра почалася! Обери режим:", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("Правда", callback_data="type_truth"), 
         InlineKeyboardButton("Дія", callback_data="type_dare")]
    ]))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    # Визначаємо, що обрали
    if "type_" in data:
        task_type = data.split("_")[1]
        task = random.choice(truths) if task_type == "truth" else random.choice(dares)
        
        scale_keyboard = [
            [InlineKeyboardButton(str(i), callback_data=f"level_{i}") for i in range(1, 6)]
        ]
        
        await query.edit_message_text(f"🔥 Ти обрав {task_type.upper()}:\n{task}\n\nОціни реакцію:", 
                                      reply_markup=InlineKeyboardMarkup(scale_keyboard))

async def scale_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    level = query.data.split("_")[1]
    await query.edit_message_text(f"🌡 Твій рівень збудження: {level}/5")

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^type_"))
    app.add_handler(CallbackQueryHandler(scale_handler, pattern="^level_"))
    app.run_polling()
