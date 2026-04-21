import os
import time
import yt_dlp

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# 🔑 TOKEN
TOKEN = "7982412181:AAEzfJvDsNIUlTCSnWaNERzpPJpdUXavmSw"

# 📥 Download function
def download_media(url):
    filename = f"file_{int(time.time())}.%(ext)s"

    ydl_opts = {
        'outtmpl': filename,
        'format': 'best',
        'quiet': True,
        'noplaylist': False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    return info


# 🟢 Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 *Ultra V10 Bot*\n\nSend Instagram / YouTube link",
        parse_mode="Markdown"
    )


# 📩 Message handler (button show)
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "http" not in text:
        return await update.message.reply_text("❌ Send valid link")

    keyboard = [
        [InlineKeyboardButton("⬇️ Download", callback_data=text)],
    ]

    await update.message.reply_text(
        "🎬 Ready to download",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# 🎯 Button click handler
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = query.data
    msg = await query.message.reply_text("⏳ Downloading...")

    try:
        info = download_media(url)

        title = info.get("title", "Downloaded File")

        # 📸 Carousel
        if 'entries' in info:
            media = []
            for entry in info['entries']:
                file = entry['requested_downloads'][0].get('filepath') or entry['requested_downloads'][0].get('filename')
                media.append(InputMediaPhoto(open(file, "rb")))

            await query.message.reply_media_group(media)
            await msg.edit_text("✅ Done (Carousel)")
            return

        file = info['requested_downloads'][0].get('filepath') or info['requested_downloads'][0].get('filename')

        size = round(os.path.getsize(file) / (1024 * 1024), 2)

        caption = f"📌 {title}\n📦 Size: {size} MB"

        # 🎥 Video
        if file.endswith(".mp4"):
            await query.message.reply_video(open(file, "rb"), caption=caption)

        # 🖼️ Image
        elif file.endswith((".jpg", ".jpeg", ".png")):
            await query.message.reply_photo(open(file, "rb"), caption=caption)

        else:
            await query.message.reply_document(open(file, "rb"), caption=caption)

        await msg.edit_text("✅ Done")

    except Exception as e:
        await msg.edit_text(f"❌ Error:\n{str(e)}")


# 🚀 Run
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
app.add_handler(CallbackQueryHandler(button))

print("🔥 Ultra V10 Running...")
app.run_polling()
