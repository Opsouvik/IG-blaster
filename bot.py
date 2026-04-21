import os
import time
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.getenv("7982412181:AAHvgTQXyEYl6gixkYYi8hf17lLxek0vB6U")

progress_message = None

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Instagram Pro Max Bot\nSend link 🔗")

# PROGRESS HOOK
def progress_hook(d):
    global progress_message
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%')
        try:
            if progress_message:
                progress_message.edit_text(f"📥 Downloading... {percent}")
        except:
            pass

# HANDLE LINK
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if "instagram.com" not in url:
        await update.message.reply_text("❌ Invalid Instagram link")
        return

    context.user_data["url"] = url

    keyboard = [[InlineKeyboardButton("📥 Download", callback_data="download")]]

    await update.message.reply_text(
        "Click to download:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# BUTTON CLICK
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global progress_message

    query = update.callback_query
    await query.answer()

    url = context.user_data.get("url")

    progress_message = await query.edit_message_text("⏳ Starting...")

    filename = f"ig_{int(time.time())}.%(ext)s"

    try:
        ydl_opts = {
            'outtmpl': filename,
            'quiet': True,
            'progress_hooks': [progress_hook]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        await progress_message.edit_text("✅ Download complete! Uploading...")

        # CAROUSEL
        if 'entries' in info:
            media = []

            for entry in info['entries']:
                file = ydl.prepare_filename(entry)

                if file.endswith(".mp4"):
                    await query.message.reply_video(video=open(file, "rb"))
                else:
                    media.append(InputMediaPhoto(open(file, "rb")))

            if media:
                await query.message.reply_media_group(media)

        else:
            file = ydl.prepare_filename(info)
            size = os.path.getsize(file)

            if size > 50 * 1024 * 1024:
                await query.message.reply_document(
                    document=open(file, "rb"),
                    caption="📦 Large file"
                )
            else:
                if file.endswith(".mp4"):
                    await query.message.reply_video(video=open(file, "rb"))
                else:
                    await query.message.reply_photo(photo=open(file, "rb"))

        # CLEANUP
        for f in os.listdir():
            if f.startswith("ig_"):
                os.remove(f)

        await progress_message.delete()

    except Exception as e:
        await progress_message.edit_text(f"❌ Error:\n{str(e)}")

# MAIN
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(button_click))

    print("🔥 IG PRO MAX RUNNING...")

    app.run_polling()

if __name__ == "__main__":
    main()
