import os
import asyncio
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import aiohttp

TELEGRAM_TOKEN = '7576082688:AAE7B5p24JklJiIXEihrF2Fu7f7SgjIvnCc'
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Immagini profilo divertenti da URL (puoi usarle direttamente)
PROFILE_PICS = [
    "https://i.imgur.com/Peq3Fk1.png",  # immagine sorridente robot
    "https://i.imgur.com/6p6B1wv.png",  # immagine buffa pupazzo
    "https://i.imgur.com/eIA3v7C.png",  # immagine animata smile felice
]

async def change_profile_photo_periodically(application: ApplicationBuilder):
    bot: Bot = application.bot
    index = 0
    while True:
        url = PROFILE_PICS[index % len(PROFILE_PICS)]
        index += 1

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                img_bytes = await resp.read()
        with open("tmp_profile_pic.jpg", "wb") as f:
            f.write(img_bytes)

        with open("tmp_profile_pic.jpg", "rb") as photo:
            try:
                await bot.set_my_commands([])
                await bot.set_user_profile_photos(photo)
                print(f"Foto profilo cambiata: {url}")
            except Exception as e:
                print(f"Errore cambio foto profilo: {e}")

        await asyncio.sleep(3600)  # cambia ogni ora

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎶 Ciao! Mandami un link e ti scarico la migliore musica! 🚀")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📩 Mandami un link di YouTube o altro, riceverai un MP3 favoloso!")

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

    await update.message.reply_text(f"🎧 Ci penso io, {user_first_name}! Scarico la musica...")

    file_path = os.path.join(DOWNLOAD_DIR, f"{chat_id}.mp3")
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, download_media, url, file_path)
        with open(file_path, 'rb') as audio_file:
            await update.message.reply_audio(audio_file, title="Eccoti la tua hit! 🔥")
        os.remove(file_path)
        await update.message.reply_text("🎉 Ecco qua! Goditi la musica e torna presto! 😉")
    except Exception as e:
        await update.message.reply_text(f"😞 Ops, c’è stato un problema: {e}")

async def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.job_queue.run_repeating(lambda _: change_profile_photo_periodically(application), interval=3600, first=10)

    print("🟢 Bot avviato!")
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
