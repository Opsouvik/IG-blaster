from telegram import Update, InputMediaPhoto
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import yt_dlp
import glob
import os

TOKEN = "8703423683:AAG28z2dCDkcZl3o29Lt9SCF1m3NvDdPPlA"

# ---------- Get latest downloaded file ----------
def get_latest():
    files = glob.glob("*")
    files = [f for f in files if f.endswith((".mp4", ".jpg", ".png", ".jpeg"))]
    if not files:
        return None
    return max(files, key=os.path.getctime)

# ---------- Downloader ----------
async def downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # ❌ Ignore commands like /start
    if text.startswith("/"):
        await update.message.reply_text("Send a valid link 😊")
        return

    # ❌ Invalid link check
    if not text.startswith("http"):
        await update.message.reply_text("Send a valid link 😊")
        return

    msg = await update.message.reply_text("⏳ Processing...")

    try:
        ydl_opts = {
            'outtmpl': 'video_%(id)s.%(ext)s',
            'format': 'best',
            'quiet': True,
            'noplaylist': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(text, download=True)

        file = get_latest()

        if not file:
            await msg.edit_text("❌ No media found")
            return

        # 🎥 Send video
        if file.endswith(".mp4"):
            await update.message.reply_video(video=open(file, "rb"))
        else:
            await update.message.reply_photo(photo=open(file, "rb"))

        await msg.edit_text("✅ Download complete!")

        # 🧹 Clean file after sending
        os.remove(file)

    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")

# ---------- Run bot ----------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, downloader))

print("Bot running...")
app.run_polling()
