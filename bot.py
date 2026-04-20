from telegram import Update, InputMediaPhoto
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import yt_dlp
import time
import os
import glob
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

TOKEN = "8703423683:AAG28z2dCDkcZl3o29Lt9SCF1m3NvDdPPlA"

progress_msg = None

def progress_hook(d):
    global progress_msg
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%')
        try:
            if progress_msg:
                progress_msg.edit_text(f"📥 Downloading... {percent}")
        except:
            pass

def get_latest():
    files = glob.glob("video_*") + glob.glob("*.jpg") + glob.glob("*.png") + glob.glob("*.mp4")
    return sorted(files, key=os.path.getctime)

async def downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global progress_msg
    text = update.message.text.strip()

    # ✅ Fix 1: command ignore
    if text.startswith("/"):
        await update.message.reply_text("Send a valid link 😄")
        return

    progress_msg = await update.message.reply_text("⏳ Processing...")

    try:
        filename = f"video_{int(time.time())}.%(ext)s"

        ydl_opts = {
            'outtmpl': filename,
            'format': 'best',
            'progress_hooks': [progress_hook],
            'quiet': True,
            'noplaylist': False
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(text, download=True)

        await progress_msg.edit_text("✅ Download complete")

        # ✅ Fix 2: safe media handling
        if 'entries' in info:
            media = []
            for entry in info['entries']:
                try:
                    file = ydl.prepare_filename(entry)
                    if os.path.exists(file):
                        media.append(InputMediaPhoto(open(file, 'rb')))
                except:
                    pass

            if media:
                await update.message.reply_media_group(media)
            else:
                await update.message.reply_text("❌ No media found")

        else:
            file = ydl.prepare_filename(info)

            if os.path.exists(file):
                await update.message.reply_document(open(file, 'rb'))
            else:
                await update.message.reply_text("❌ File not found")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# 🔥 Render port fix (fake web server)
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running')

def run_web():
    server = HTTPServer(('0.0.0.0', 10000), Handler)
    server.serve_forever()

threading.Thread(target=run_web).start()

# 🔥 Telegram bot start
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT, downloader))

app.run_polling()
