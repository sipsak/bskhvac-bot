import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from flask import Flask
import threading
import aiohttp
import time
import os
import cv2
import numpy as np
from pyzbar.pyzbar import decode

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

def preprocess_image_for_barcode(image_path):
    """
    Barkod/QR kod okuma performansını artırmak için görüntüyü ön işlemden geçirir.
    """
    # Görüntüyü oku
    image = cv2.imread(image_path)
    if image is None:
        return None
    
    # Gri tonlamaya çevir
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Görüntüyü iyileştirme denemeleri
    processed_images = []
    
    # 1. Orijinal gri tonlamalı görüntü
    processed_images.append(gray)
    
    # 2. Gauss bulanıklaştırma
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    processed_images.append(blurred)
    
    # 3. Kontrastı artır
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    processed_images.append(enhanced)
    
    # 4. Threshold uygulama
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    processed_images.append(thresh)
    
    # 5. Adaptif threshold
    adaptive_thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    processed_images.append(adaptive_thresh)
    
    return processed_images

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
            # Görüntüyü ön işlemden geçir
            processed_images = preprocess_image_for_barcode(photo_path)
            
            if not processed_images:
                await update.message.reply_text("Görsel işlenemedi.")
                return
            
            # Tüm işlenmiş görüntülerde barkod/QR kod ara
            for img in processed_images:
                decoded_objects = decode(img)
                
                if decoded_objects:
                    code = decoded_objects[0].data.decode("utf-8")
                    logging.info(f"Barkod başarıyla okundu: {code}")
                    await get_image_by_code(update, code)
                    return
            
            # Hiçbir işleme yönteminde barkod bulunamadıysa
            await update.message.reply_text("Barkod/QR kod okunamadı. Lütfen daha net bir fotoğraf çekmeyi deneyin.")
            
        except Exception as e:
            logging.exception("Barkod çözümleme hatası")
            await update.message.reply_text("Görsel işlenemedi. Lütfen başka bir fotoğraf deneyin.")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, handle_message))

    app.run_polling()
