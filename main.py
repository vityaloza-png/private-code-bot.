 import os
import random
import threading
import logging
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==========================================
# 1. НАЛАШТУВАННЯ ТА БАЗА ДАНИХ
# ==========================================
logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("TOKEN")

waiting_players = []
# Тепер games зберігає не просто ID, а цілу "сесію"
# games[user_id] = {"partner": id, "turn": id_того_хто_задає_питання, "state": "ask" або "answer"}
games = {} 

DISTANCE_QUESTIONS = [
    "Яка твоя найсміливіша сексуальна фантазія?",
    "Що б ти зі мною зробив(ла), якби ми зараз були поруч?",
    "Яка частина тіла тебе найбільше збуджує?",
]

TRUTH_QUESTIONS = [
    "Чи був у тебе досвід з кількома партнерами одночасно?",
    "Який найбожевільніший вчинок у ліжку ти робив(ла)?",
    "Про що ти думаєш, коли задовольняєш себе?",
]

DARE_ACTIONS = [
    "Повільно зніми з мене одну річ.",
    "Зроби мені масаж там, де захочеш.",
    "Поцілуй мене в найчутливіше місце.",
]

# ==========================================
# 2. FLASK (ОБМАНКА ДЛЯ RENDER)
# ==========================================
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

# ==========================================
# 3. ЛОГІКА БОТА ТА КЛАВІАТУРИ
# ==========================================
def get_active_keyboard():
    """Кнопки для того, чия черга ЗАДАВАТИ питання"""
    keyboard = [
        ["🎲 Правда чи Дія", "❓ Питання"],
        ["⏹ Стоп"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_waiting_keyboard():
    """Кнопки для того, хто ВІДПОВІДАЄ (кнопок питань нема)"""
    keyboard = [
        ["⏹ Стоп"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("✅ Приєднатися до гри", callback_data='join_game')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Вітаю! Натисни кнопку, щоб знайти партнера.", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    await query.answer()

    if query.data == 'join_game':
        if user.id in waiting_players or user.id in games:
            await query.edit_message_text("Ти вже в черзі або в грі!")
            return

        waiting_players.append(user.id)
        await query.edit_message_text(f"Ти в черзі! Шукаємо партнера...")

        if len(waiting_players) >= 2:
            p1 = waiting_players.pop(0)
            p2 = waiting_players.pop(0)
            
            # Створюємо спільну сесію. Черга починається з гравця 1.
            session = {
                "p1": p1,
                "p2": p2,
                "turn": p1, 
                "state": "ask"  # Стан гри: очікування вибору питання
            }
            games[p1] = session
            games[p2] = session
            
            # Відправляємо різні клавіатури
            await context.bot.send_message(p1, "🔥 Гру розпочато!\n**Твоя черга!** Обирай категорію:", reply_markup=get_active_keyboard(), parse_mode="Markdown")
            await context.bot.send_message(p2, "🔥 Гру розпочато!\n**Зараз черга партнера** задавати питання. Чекай...", reply_markup=get_waiting_keyboard(), parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if user_id not in games:
        return

    session = games[user_id]
    partner_id = session["p2"] if session["p1"] == user_id else session["p1"]

    # 1. ОБРОБКА СТОП
    if text == "⏹ Стоп":
        await context.bot.send_message(partner_id, "Партнер завершив гру. Шукаємо нового...", reply_markup=ReplyKeyboardRemove())
        await context.bot.send_message(user_id, "Гру завершено.", reply_markup=ReplyKeyboardRemove())
        del games[user_id]
        if partner_id in games:
            del games[partner_id]
        return

    # 2. ЯКЩО СТАН "ЗАДАВАТИ ПИТАННЯ" (ASK)
    if session["state"] == "ask":
        # Якщо хтось пише не в свою чергу
        if session["turn"] != user_id:
            await update.message.reply_text("Зараз не твоя черга задавати питання! Чекай.")
            return

        # Генерація питання в залежності від кнопки
        msg = ""
        if text == "❓ Питання":
            question = random.choice(DISTANCE_QUESTIONS)
            msg = f"📩 Питання:\n\n*«{question}»*"
        elif text == "🎲 Правда чи Дія":
            if random.choice(["Правда", "Дія"]) == "Правда":
                msg = f"🗣 **ПРАВДА**:\n\n*«{random.choice(TRUTH_QUESTIONS)}»*"
            else:
                msg = f"😈 **ДІЯ**:\n\n*«{random.choice(DARE_ACTIONS)}»*"
        else:
            await update.message.reply_text("Будь ласка, використай кнопки на клавіатурі.")
            return

        # Надсилаємо питання обом, змінюємо стан на очікування відповіді
        session["state"] = "answer"
        
        await context.bot.send_message(user_id, f"Ти задав:\n{msg}\n\n⏳ _Чекаємо відповідь від партнера..._", reply_markup=get_waiting_keyboard(), parse_mode="Markdown")
        await context.bot.send_message(partner_id, f"Тобі випало:\n{msg}\n\n✍️ **Напиши свою відповідь у чат!**", reply_markup=get_waiting_keyboard(), parse_mode="Markdown")
        return

    # 3. ЯКЩО СТАН "ОЧІКУВАННЯ ВІДПОВІДІ" (ANSWER)
    if session["state"] == "answer":
        # Відповідати має той, чия НЕ черга задавати питання
        if session["turn"] == user_id:
            await update.message.reply_text("Чекай, поки партнер напише відповідь!")
            return

        # Отримали відповідь від партнера, пересилаємо тому, хто питав
        await context.bot.send_message(partner_id, f"💬 **Відповідь партнера:**\n_{text}_", parse_mode="Markdown")
        
        # --- МІНЯЄМО ЧЕРГУ ---
        session["turn"] = user_id # Тепер черга того, хто щойно відповідав
        session["state"] = "ask"
        
        # Оновлюємо клавіатури
        await context.bot.send_message(user_id, "✅ Твоя черга! Обирай наступне питання:", reply_markup=get_active_keyboard())
        await context.bot.send_message(partner_id, "⏳ Твій партнер обирає питання. Чекай...", reply_markup=get_waiting_keyboard())

# ==========================================
# 4. ЗАПУСК
# ==========================================
if __name__ == '__main__':
    threading.Thread(target=run_web, daemon=True).start()
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CallbackQueryHandler(button_callback))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущено!")
    bot_app.run_polling()
