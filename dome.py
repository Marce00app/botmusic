import os
import asyncio
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, JobQueue
)
import yt_dlp
import aiohttp

TELEGRAM_TOKEN = '7576082688:AAE7B5p24JklJiIXEihrF2Fu7f7SgjIvnCc'
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

PROFILE_PICS = [
    "https://i.imgur.com/Peq3Fk1.png",
    "https://i.imgur.com/6p6B1wv.png",
    "https://i.imgur.com/eIA3v7C.png",
]

async def change_profile_photo(context: ContextTypes.DEFAULT_TYPE):
    bot: Bot = context.bot
    if not hasattr(context.job, 'index'):
        context.job.index = 0
    url = PROFILE_PICS[context.job.index % len(PROFILE_PICS)]
    context.job.index += 1

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            img_bytes = await resp.read()

    with open("tmp_profile_pic.jpg", "wb") as f:
        f.write(img_bytes)

    with open("tmp_profile_pic.jpg", "rb") as photo:
        try:
            await bot.set_my_commands([])  # pulizia (facoltativo)
            await bot.set_user_profile_photos(photo)
            print(f"Foto profilo cambiata a: {url}")
        except Exception as e:
            print(f"Errore nel cambio foto profilo: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎶 Ciao! Mandami un link e ti scarico la musica! 🚀")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📩 Inviami un link YouTube o simili e ti spedisco un MP3!")

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
        'cookiesfrombrowser': ('chrome',),
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    chat_id = update.message.chat_id
    user_first_name = update.message.from_user.first_name or "amico"

    await update.message.reply_text(f"🎧 Sto scaricando la musica per te, {user_first_name}...")

    file_path = os.path.join(DOWNLOAD_DIR, f"{chat_id}.mp3")
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, download_media, url, file_path)
        with open(file_path, 'rb') as audio_file:
            await update.message.reply_audio(audio_file, title="Ecco la tua hit! 🔥")
        os.remove(file_path)
        await update.message.reply_text("🎉 Fatto! Buon ascolto! Torna presto 😉")
    except Exception as e:
        await update.message.reply_text(f"😞 Ops, errore: {e}")

def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Aggiungi job queue per cambiare foto profilo ogni ora
    job_queue: JobQueue = application.job_queue
    job_queue.run_repeating(change_profile_photo, interval=3600, first=10)

    print("🟢 Bot avviato!")
    application.run_polling()

if __name__ == "__main__":
    main()


