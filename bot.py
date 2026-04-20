from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import glob
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

TOKEN = "8703423683:AAG28z2dCDkcZl3o29Lt9SCF1m3NvDdPPlA"

# ---------- KEEP ALIVE ----------
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_web():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

threading.Thread(target=run_web, daemon=True).start()

# ---------- GET FILE ----------
def get_file():
    files = glob.glob("*")
    files = [f for f in files if f.endswith((".mp4", ".jpg", ".png", ".jpeg", ".mp3"))]
    if not files:
        return None
    return max(files, key=os.path.getctime)

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Send any link\n\n"
        "🎥 Normal = video\n"
        "🎵 /audio + link = audio"
    )

# ---------- DOWNLOADER ----------
async def downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # audio mode
    audio_mode = False
    if text.startswith("/audio"):
        audio_mode = True
        text = text.replace("/audio", "").strip()

    if not text.startswith("http"):
        await update.message.reply_text("❌ Send valid link")
        return

    msg = await update.message.reply_text("⏳ Processing...")

    try:
        ydl_opts = {
            'outtmpl': 'file_%(id)s.%(ext)s',
            'quiet': True,
            'noplaylist': True
        }

        if audio_mode:
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3'
                }]
            })
        else:
            ydl_opts.update({'format': 'best'})

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(text, download=True)

        file = get_file()

        if not file:
            await msg.edit_text("❌ No media found")
            return

        # send
        if file.endswith(".mp4"):
            await update.message.reply_video(video=open(file, "rb"))
        elif file.endswith(".mp3"):
            await update.message.reply_audio(audio=open(file, "rb"))
        else:
            await update.message.reply_photo(photo=open(file, "rb"))

        await msg.edit_text("✅ Done!")

        os.remove(file)

    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")

# ---------- RUN ----------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, downloader))

print("🔥 Bot Running...")
app.run_polling(close_loop=False)
