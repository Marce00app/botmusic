import os
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import yt_dlp

# Inserisci qui il token del tuo bot Telegram
TELEGRAM_TOKEN = '7576082688:AAE7B5p24JklJiIXEihrF2Fu7f7SgjIvnCc'

# Cartella temporanea per i download
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Ciao! Inviami qualsiasi link di video o musica e lo scaricherò per te!")

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text("Inviami un link da cui vuoi scaricare musica o video.\n"
                              "Supporto YouTube, Vimeo, SoundCloud e molto altro.")

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

def handle_message(update: Update, context: CallbackContext):
    url = update.message.text.strip()
    chat_id = update.message.chat_id

    update.message.reply_text("Scarico per te... Potrebbe volerci un attimo.")

    # Nome del file temporaneo (userID + hash o timestamp)
    file_path = os.path.join(DOWNLOAD_DIR, f"{chat_id}.mp3")
    try:
        download_media(url, file_path)

        with open(file_path, 'rb') as audio_file:
            update.message.reply_audio(audio_file, title="Ecco la tua musica 🎵")

        # Rimuovo file dopo invio
        os.remove(file_path)

    except Exception as e:
        update.message.reply_text(f"Errore durante il download: {str(e)}")

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
