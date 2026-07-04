 import os
from telegram.ext import ApplicationBuilder

# Отримуємо токен з змінних середовища (налаштуйте це в Render Dashboard)
TOKEN = os.getenv("8671245475:AAFEslZmW0ih6hYQm0wupTd3SVqoyzdvFm8")
PORT = int(os.environ.get("PORT", "8080"))

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Додайте сюди свої хендлери (наприклад: application.add_handler(...))

    # Запуск через Webhook (найкраще для Render)
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"https://ВАШ_САЙТ_НА_RENDER.onrender.com/{TOKEN}"
    )
