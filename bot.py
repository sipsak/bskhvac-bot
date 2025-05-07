import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from flask import Flask
import threading
import aiohttp
import time
import os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Flask app for health check
flask_app = Flask(__name__)

@flask_app.route('/health')
def health():
    return "OK", 200

def run_flask():
    flask_app.run(host="0.0.0.0", port=5000)

# Telegram bot handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ürün kodunu gönder, sana görselini göndereyim.")

async def get_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_code = update.message.text.strip()
    extensions = ['jpg', 'png', 'webp']
    timestamp = int(time.time())  # cache'i kırmak için
    
    # URL'ye zaman damgası ekleniyor
    url_with_cache_buster = lambda ext: f"https://bskhavalandirma.neocities.org/images/{product_code}.{ext}?v={timestamp}"

    async with aiohttp.ClientSession() as session:
        for ext in extensions:
            url = url_with_cache_buster(ext)
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        await update.message.reply_photo(photo=url)
                        return
            except Exception:
                continue

    await update.message.reply_text("Görsel bulunamadı.")

if __name__ == "__main__":
    # Start Flask in separate thread
    threading.Thread(target=run_flask, daemon=True).start()

    # Start Telegram bot
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_image))

    app.run_polling()
