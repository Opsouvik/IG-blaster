from telegram import Update, InputMediaPhoto
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import yt_dlp
import time
import os
import glob

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
    files = glob.glob("video_*") + glob.glob("audio_*")
    return sorted(files, key=os.path.getctime)[-1]

async def downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global progress_msg
    text = update.message.text

    try:
        progress_msg = await update.message.reply_text("⏳ Starting download...")

        # 🎧 MP3 MODE
        if text.startswith("mp3"):
            url = text.replace("mp3 ", "")
            filename = f"audio_{int(time.time())}.%(ext)s"

            ydl_opts = {
                'outtmpl': filename,
                'format': 'bestaudio/best',
                'progress_hooks': [progress_hook],
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3'
                }]
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            file = get_latest()
            await progress_msg.edit_text("✅ Done! Sending MP3...")
            await update.message.reply_audio(audio=open(file, "rb"))

        # 🎥 VIDEO / INSTAGRAM
        else:
            url = text
            filename = f"video_{int(time.time())}.%(ext)s"

            ydl_opts = {
                'outtmpl': filename,
                'format': 'best',
                'progress_hooks': [progress_hook]
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)

                await progress_msg.edit_text("✅ Download complete!")

                # 📸 Carousel
                if 'entries' in info:
                    media = []
                    for entry in info['entries']:
                        file = ydl.prepare_filename(entry)
                        media.append(InputMediaPhoto(open(file, "rb")))

                    await update.message.reply_media_group(media)

                else:
                    file = ydl.prepare_filename(info)

                    if file.endswith(".mp4"):
                        await update.message.reply_video(video=open(file, "rb"))
                    else:
                        await update.message.reply_photo(photo=open(file, "rb"))

    except Exception as e:
        await update.message.reply_text("❌ Error:\n" + str(e))

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT, downloader))

app.run_polling()

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running')

def run_web():
    server = HTTPServer(('0.0.0.0', 10000), Handler)
    server.serve_forever()

threading.Thread(target=run_web).start()
