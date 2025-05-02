from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Bot Token'ını buraya girin
BOT_TOKEN = '7284877871:AAGTXfc62DGC7s14qeqkMiLFJsIrSeDPLGs'

# Görsel URL yapısı
IMAGE_BASE_URL = "https://bskhavalandirma.neocities.org/images/"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ürün kodunu gönder, sana görselini atayım.")

async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip()
    for ext in ['jpg', 'png', 'webp']:
        image_url = f"{IMAGE_BASE_URL}{code}.{ext}"
        try:
            await update.message.reply_photo(photo=image_url)
            return
        except:
            continue
    await update.message.reply_text("Bu ürün koduna ait görsel bulunamadı.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))
    app.run_polling()
