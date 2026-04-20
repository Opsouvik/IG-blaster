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
    files = glob.glob("video_*") + glob.glob("*.jpg") + glob.glob("*.png")
    return sorted(files, key=os.path.getctime)

async def downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global progress_msg
    text = update.message.text

    progress_msg = await update.message.reply_text("⏳ Processing...")

    try:
        filename = f"video_{int(time.time())}.%(ext)s"

        ydl_opts = {
            'outtmpl': filename,
            'format': 'best',
            'progress_hooks': [progress_hook]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(text, download=True)

        await progress_msg.edit_text("✅ Download complete")

        if 'entries' in info:
            media = []
            for entry in info['entries']:
                file = ydl.prepare_filename(entry)
                media.append(InputMediaPhoto(open(file, 'rb')))
            await update.message.reply_media_group(media)
        else:
            file = ydl.prepare_filename(info)
            await update.message.reply_document(open(file, 'rb'))

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# 🔥 Web server (Render fix)
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
