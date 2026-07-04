from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import random
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

def run_http_server():
    server = HTTPServer(('0.0.0.0', 8080), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_http_server, daemon=True).start()

# Встав сюди свій НОВИЙ токен (який ти отримав після /revoke)
TOKEN = '8671245475:AAFEslZmW0ih6hYQm0wupTd3SVqoyzdvFm8'

# База питань (можеш сюди вписати будь-яку кількість)
questions = [
    "Який твій найулюбленіший спогад про нашу першу зустріч?",
    "Яку рису мого характеру ти цінуєш понад усе?",
    "Якби ми могли поїхати в подорож прямо зараз, куди б ти хотів(ла) вирушити?",
    "Який фільм у тебе асоціюється зі мною?",
    "Розкажи про момент, коли ти зрозумів(ла), що ми — ідеальна пара.",
    "Який найприємніший комплімент ти отримував(ла) від мене?"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [['🎯 Нове питання', '🔄 Статистика'], ['💬 Режим спілкування']]
    await update.message.reply_text(
        "✨ Private Code активовано. Обирай дію:", 
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )

async def game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == '🎯 Нове питання':
        await update.message.reply_text(f"❓ Питання: {random.choice(questions)}")
        
    elif text == '🔄 Статистика':
        await update.message.reply_text("Ми продовжуємо дізнаватися одне одного краще!")
        
    elif text == '💬 Режим спілкування':
        await update.message.reply_text("Режим чату увімкнено. Пишіть, я не втручаюся!")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), game))
    app.run_polling()
