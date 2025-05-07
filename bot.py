import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from flask import Flask
import threading
import aiohttp
import time
import os
import subprocess

logging.basicConfig(
    filename='/app/bot_logs.log',
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

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; bskhvac-bot/1.0)"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        for ext in extensions:
            url = url_with_cache_buster(ext)
            logging.info(f"Denetlenen URL: {url}")
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        await update.message.reply_photo(photo=url)
                        return
            except Exception as e:
                logging.warning(f"{url} adresine erişilemedi: {e}")
                continue

    await update.message.reply_text("Görsel bulunamadı.")

async def decode_barcode_with_zxing(image_path):
    try:
        result = subprocess.run(
            [
                "java",
                "-cp",
                "/app/core-3.5.2.jar:/app/javase-3.5.2.jar:/app/jcommander.jar",
                "com.google.zxing.client.j2se.CommandLineRunner",
                image_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if result.returncode != 0:
            logging.error(f"ZXing hata kodu: {result.returncode}")
            logging.error(f"ZXing stderr: {result.stderr.decode('utf-8')}")
            return None

        output = result.stdout.decode("utf-8").strip()
        logging.info(f"ZXing çıktı: {output}")

        return output.splitlines()[0] if output else None

    except Exception as e:
        logging.exception("ZXing çalıştırılırken hata oluştu")
        return None

        output = result.stdout.decode("utf-8").strip()
        logging.info(f"ZXing çıktı: {output}")

        return output.splitlines()[0] if output else None

    except Exception as e:
        logging.exception("ZXing çalıştırılırken hata oluştu")
        return None

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
            
        decoded_text = await decode_barcode_with_zxing(photo_path)
        
        if not decoded_text:
            await update.message.reply_text("Barkod/QR kod okunamadı.")
            return
            
        code = decoded_text.strip()  # Temizle ve kodu ayıkla
        logging.info(f"Çözümlenen ürün kodu: {code}")
        
        await get_image_by_code(update, code)

        except Exception as e:
            logging.exception("Görsel işleme hatası")
            await update.message.reply_text("Görsel işlenemedi.")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, handle_message))

    app.run_polling()
