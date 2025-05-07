import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from flask import Flask
import threading
import aiohttp
import time
import os
from PIL import Image
import zxing  # Changed from pyzbar to zxing

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ürün kodunu ya da barkod görselini gönder, sana görselini göndereyim.")

async def get_image_by_code(update: Update, code: str):
    extensions = ['jpg', 'png', 'webp']
    timestamp = int(time.time())
    url_with_cache_buster = lambda ext: f"https://bskhavalandirma.neocities.org/images/{code}.{ext}?v={timestamp}"

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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text:
        code = update.message.text.strip()
        await get_image_by_code(update, code)

    elif update.message.photo:
        photo = update.message.photo[-1]  # En yüksek çözünürlüklü olanı al
        photo_file = await photo.get_file()
        photo_path = "/tmp/barkod.jpg"
        await photo_file.download_to_drive(photo_path)

        try:
            # Create a ZXing reader
            reader = zxing.BarCodeReader()
            
            # Decode the image
            barcode = reader.decode(photo_path)
            
            if barcode and barcode.parsed:
                code = barcode.parsed
                await get_image_by_code(update, code)
            else:
                await update.message.reply_text("Barkod/QR kod okunamadı.")
                
        except Exception as e:
            logging.exception("Barkod çözümleme hatası")
            await update.message.reply_text("Görsel işlenemedi.")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, handle_message))

    app.run_polling()
