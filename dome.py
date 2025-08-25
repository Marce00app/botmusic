
import os
import asyncio
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes
)
import yt_dlp

TELEGRAM_TOKEN = '7576082688:AAE7B5p24JklJiIXEihrF2Fu7f7SgjIvnCc'
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(id)s.%(ext)s',
    'quiet': True,
    'no_warnings': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'noplaylist': True,
    'cachedir': False,
    'cookies': 'cookies.txt',  # Usa il file cookies.txt
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎶 Ciao! Inviami un link YouTube o altro video e ti scarico la musica! 🚀")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📩 Inviami un link video e ti rispondo con il file MP3!")

def download_media(url, output_path):
    opts = dict(ydl_opts)  # copia per modificare outtmpl
    opts['outtmpl'] = output_path
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    chat_id = update.message.chat_id
    user_first_name = update.message.from_user.first_name or "amico"

    await update.message.reply_text(f"🎧 Scarico la musica per te, {user_first_name}! 🚀")

    file_path = os.path.join(DOWNLOAD_DIR, f"{chat_id}.mp3")
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, download_media, url, file_path)
        with open(file_path, 'rb') as audio_file:
            await update.message.reply_audio(audio_file, title="Ecco la tua hit! 🔥")
        os.remove(file_path)
        await update.message.reply_text("🎉 Ecco qua! Buon ascolto! 🔥")
    except Exception as e:
        await update.message.reply_text(f"😞 Ops, c’è stato un problema: {e}")

def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🟢 Bot avviato!")
    application.run_polling()

if __name__ == "__main__":
    main()
