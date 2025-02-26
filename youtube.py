import os
import subprocess
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, CallbackContext, filters

TOKEN = "6849473588:AAHKCSjNPD_Po7D86lDnw9nDlvbJyt7mQPs"
DB_FILE = "baza.txt"
LOG_FILE = "log.txt"
LIMIT = 10  # Kunlik limit

def load_users():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_users(users):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

def log_message(message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    print(message)

async def start(update: Update, context: CallbackContext):
    users = load_users()
    user_id = str(update.message.from_user.id)

    if user_id not in users:
        users[user_id] = {"limit": LIMIT, "links": []}
        save_users(users)
    
    await update.message.reply_text("🎥 YouTube video havolasini yuboring!")

async def get_video_info(update: Update, context: CallbackContext):
    users = load_users()
    user_id = str(update.message.from_user.id)
    url = update.message.text.strip()

    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("❌ Iltimos, faqat YouTube havolasini yuboring.")
        return
    
    if user_id not in users:
        await update.message.reply_text("❌ Iltimos, avval /start buyrug'ini bosing.")
        return
    
    if users[user_id]["limit"] <= 0:
        await update.message.reply_text("🚫 Kunlik limit tugadi. Ertaga qayta urinib ko'ring!")
        return

    users[user_id]["links"].append({"url": url, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    save_users(users)

    # Video haqida ma’lumot olish
    command = f'yt-dlp -J {url}'
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        video_data = json.loads(result.stdout)

        title = video_data.get("title", "Noma’lum video")
        thumbnail = video_data.get("thumbnail", None)
        duration = video_data.get("duration", "Noma’lum vaqt")
        view_count = video_data.get("view_count", "Noma’lum")
        upload_date = video_data.get("upload_date", "Noma’lum")

        # Fayl hajmlarini olish
        formats = video_data.get("formats", [])
        format_sizes = {}

        for f in formats:
            height = f.get("height")
            filesize = f.get("filesize", 0)

            if height in [360, 480, 720] and filesize:
                format_sizes[str(height)] = round(filesize / (1024 * 1024), 1)  # MB ga o‘girish

        # Tugmalar yaratish
        keyboard = [
            [InlineKeyboardButton(f"🔻📹 360p - {format_sizes.get('360', 'Noma’lum')} MB", callback_data=f"{url}|360p")],
            [InlineKeyboardButton(f"🔻📹 480p - {format_sizes.get('480', 'Noma’lum')} MB", callback_data=f"{url}|480p")],
            [InlineKeyboardButton(f"🔻📹 720p - {format_sizes.get('720', 'Noma’lum')} MB", callback_data=f"{url}|720p")],
            [InlineKeyboardButton(f"🔻🎧 Audio - Noma’lum MB", callback_data=f"{url}|audio")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = (
            f"🎬 *{title}*\n"
            f"📅 Yuklangan sana: {upload_date}\n"
            f"👀 Ko‘rishlar soni: {view_count}\n"
            f"⏰ {duration} soniya\n\n"
            f"Tanlang va yuklab oling:"
        )

        if thumbnail:
            await update.message.reply_photo(photo=thumbnail, caption=text, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    except Exception as e:
        log_message(f"Xatolik: {e}")
        await update.message.reply_text("❌ Video ma'lumotlarini olishda xatolik yuz berdi.")

async def download_video(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    users = load_users()

    if user_id not in users:
        await query.message.reply_text("❌ Iltimos, avval /start buyrug'ini bosing.")
        return

    if users[user_id]["limit"] <= 0:
        await query.message.reply_text("🚫 Kunlik limit tugadi. Ertaga qayta urinib ko'ring!")
        return

    users[user_id]["limit"] -= 1
    save_users(users)

    # Callback_data'dan URL va formatni ajratib olish
    data = query.data.split("|")
    url = data[0]
    quality = data[1]

    await query.message.reply_text(f"🔄 {quality} formatda yuklanmoqda... Bir necha soniya kuting.")

    file_ext = "mp4" if quality != "audio" else "mp3"
    video_path = f"video.{file_ext}"

    try:
        format_flag = {
            "360p": "best[height<=360]",
            "480p": "best[height<=480]",
            "720p": "best[height<=720]",
            "audio": "bestaudio"
        }

        command = f'yt-dlp -f "{format_flag[quality]}" -o "{video_path}" {url}'
        subprocess.run(command, shell=True, check=True)

        with open(video_path, "rb") as video:
            await query.message.reply_document(document=video, filename=f"video.{file_ext}")
        os.remove(video_path)
        
        log_message(f"{user_id} uchun video yuklandi: {url}, Sifat: {quality}")
    except Exception as e:
        await query.message.reply_text(f"❌ Xatolik yuz berdi: {e}")
        log_message(f"{user_id} uchun video yuklash muvaffaqiyatsiz: {url}, Xatolik: {e}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_video_info))
    app.add_handler(CallbackQueryHandler(download_video))

    print("🚀 Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
