import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# ====== CONFIG ======
TOKEN = "7982412181:AAEzfJvDsNIUlTCSnWaNERzpPJpdUXavmSw"

# ====== LOGGING ======
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ====== START ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\n\nSend me any video link 📥\nI will download & send it 🚀"
    )

# ====== HELP ======
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Commands:\n"
        "/start - Start bot\n"
        "/help - Help menu\n\n"
        "Just send a link 🔗"
    )

# ====== DOWNLOAD FUNCTION ======
def download_video(url):
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'best',
        'noplaylist': True,
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)

    return file_path

# ====== HANDLE MESSAGE ======
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    msg = await update.message.reply_text("⏳ Downloading...")

    try:
        os.makedirs("downloads", exist_ok=True)

        file_path = download_video(url)

        await msg.edit_text("📤 Uploading...")

        await update.message.reply_document(document=open(file_path, 'rb'))

        os.remove(file_path)

        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")

# ====== MAIN ======
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🤖 Bot Running...")
app.run_polling()
