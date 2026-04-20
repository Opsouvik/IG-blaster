
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv("8703423683:AAG28z2dCDkcZl3o29Lt9SCF1m3NvDdPPlA")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me a video link (YouTube / Instagram)")

async def downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # Ignore /start
    if text.startswith("/"):
        return

    if not text.startswith("http"):
        await update.message.reply_text("❌ Send a valid link 😅")
        return

    msg = await update.message.reply_text("⏳ Processing...")

    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'video.%(ext)s',
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(text, download=True)

            if 'entries' in info:
                info = info['entries'][0]

            file = ydl.prepare_filename(info)

        if not os.path.exists(file):
            await msg.edit_text("❌ No media found")
            return

        await msg.edit_text("📤 Uploading...")

        if file.endswith(".mp4"):
            await update.message.reply_video(video=open(file, 'rb'))
        else:
            await update.message.reply_document(document=open(file, 'rb'))

        os.remove(file)

    except Exception as e:
        await msg.edit_text(f"❌ Error:\n{str(e)}")

# App setup
app = ApplicationBuilder().token(TOKEN).build()

# Handlers
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, downloader))

# Run bot
print("Bot Running...")
app.run_polling()
