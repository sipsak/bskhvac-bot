import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = "7284877871:AAGTXfc62DGC7s14qeqkMiLFJsIrSeDPLGs"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ürün kodunu gönder, sana görselini göndereyim.")

async def get_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_code = update.message.text.strip()
    extensions = ['jpg', 'png', 'webp']
    for ext in extensions:
        url = f"https://bskhavalandirma.neocities.org/images/{product_code}.{ext}"
        await update.message.reply_photo(photo=url)
        return
    await update.message.reply_text("Görsel bulunamadı.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler(None, get_image))  # Her mesajı işle

    app.run_polling()
