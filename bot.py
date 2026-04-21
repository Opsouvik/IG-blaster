import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv("8703423683:AAG28z2dCDkcZl3o29Lt9SCF1m3NvDdPPlA")

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send a valid Instagram / YouTube link 😄")

# download handler
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if "http" not in url:
        await update.message.reply_text("Send a valid link 😑")
        return

    await update.message.reply_text("⏳ Processing...")

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.%(ext)s',
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # send file
        await update.message.reply_video(video=open(filename, 'rb'))

        # delete file after send
        os.remove(filename)

        await update.message.reply_text("✅ Download complete")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# main run
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

    print("Bot Running...")
    app.run_polling()
