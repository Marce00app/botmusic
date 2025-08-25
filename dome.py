import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import asyncio

TELEGRAM_TOKEN = os.getenv('7576082688:AAE7B5p24JklJiIXEihrF2Fu7f7SgjIvnCc')

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ciao! Inviami un link valido per scaricare musica o video.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Inviami un link di YouTube o altro e ti invierò la musica in MP3.")

def download_media(url, path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': path,
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': True,
        'cachedir': False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    chat_id = update.message.chat_id

    await update.message.reply_text("Scaricamento in corso, attendi...")

    file_path = os.path.join(DOWNLOAD_DIR, f"{chat_id}.mp3")
    loop = asyncio.get_event_loop()
    try:
        # Esegui il download in un thread separato per non bloccare il bot async
        await loop.run_in_executor(None, download_media, url, file_path)
        with open(file_path, 'rb') as audio_file:
            await update.message.reply_audio(audio_file, title="Ecco la tua musica 🎵")
        os.remove(file_path)
    except Exception as e:
        await update.message.reply_text(f"Errore nel download: {e}")

def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
