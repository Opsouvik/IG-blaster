import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

TOKEN = os.getenv("7982412181:AAHvgTQXyEYl6gixkYYi8hf17lLxek0vB6U")

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 Ultra Downloader Bot\n\n"
        "Send YouTube / Instagram link\n\n"
        "Commands:\n"
        "/audio - Download audio only"
    )

# Download video
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    msg = await update.message.reply_text("⏳ Downloading video...")

    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'best[ext=mp4]/best',
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        file = next((f for f in os.listdir() if f.startswith("video")), None)

        if file:
            await update.message.reply_video(video=open(file, "rb"))
            os.remove(file)

        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")

# Download audio
async def download_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use: /audio <link>")
        return

    url = context.args[0]
    msg = await update.message.reply_text("🎧 Downloading audio...")

    ydl_opts = {
        'outtmpl': 'audio.%(ext)s',
        'format': 'bestaudio',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        file = next((f for f in os.listdir() if f.startswith("audio")), None)

        if file:
            await update.message.reply_audio(audio=open(file, "rb"))
            os.remove(file)

        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("audio", download_audio))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("🚀 Bot Running...")

    app.run_polling()

if __name__ == "__main__":
    main()
