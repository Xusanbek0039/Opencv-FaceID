import os
import requests
import instaloader
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext
from datetime import datetime

# Bot tokenini shu yerga yozing
TOKEN = '6849473588:AAHKCSjNPD_Po7D86lDnw9nDlvbJyt7mQPs'

# Foydalanuvchi xizmat sanog'ini saqlash
USER_LIMIT = 1_000_000
DAILY_LIMIT = 10

if not os.path.exists("counter.txt"):
    with open("counter.txt", "w") as f:
        f.write("0")

if not os.path.exists("user_limits.txt"):
    with open("user_limits.txt", "w") as f:
        f.write("")

def get_next_request_number():
    with open("counter.txt", "r+") as f:
        count = int(f.read().strip())
        if count >= USER_LIMIT:
            return None  # Limit tugagan
        f.seek(0)
        f.write(str(count + 1))
        f.truncate()
    return count + 1

def check_user_limit(user_id, username, first_name, last_name):
    today = datetime.now().date()
    user_limits = {}
    full_name = f"{first_name or ''} {last_name or ''}".strip()
    username = username or "Nomalum"
    
    if os.path.exists("user_limits.txt"):
        with open("user_limits.txt", "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 4:
                    uid = int(parts[0])
                    user = parts[1]
                    name = " ".join(parts[2:-2])
                    count = int(parts[-2])
                    date = datetime.strptime(parts[-1], "%Y-%m-%d").date()
                    user_limits[uid] = (user, name, count, date)
    
    if user_id in user_limits:
        user, name, count, last_date = user_limits[user_id]
        if last_date == today:
            user_limits[user_id] = (user, name, count, today)
        else:
            user_limits[user_id] = (user, name, 0, today)
    else:
        user_limits[user_id] = (username, full_name, 0, today)
    
    with open("user_limits.txt", "w") as f:
        for uid, (user, name, count, date) in user_limits.items():
            f.write(f"{uid} {user} {name} {count} {date}\n")
    
    return user_limits[user_id][2], DAILY_LIMIT - user_limits[user_id][2]

def increment_user_limit(user_id, username, first_name, last_name):
    today = datetime.now().date()
    user_limits = {}
    full_name = f"{first_name or ''} {last_name or ''}".strip()
    username = username or "Nomalum"
    
    if os.path.exists("user_limits.txt"):
        with open("user_limits.txt", "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 4:
                    uid = int(parts[0])
                    user = parts[1]
                    name = " ".join(parts[2:-2])
                    count = int(parts[-2])
                    date = datetime.strptime(parts[-1], "%Y-%m-%d").date()
                    user_limits[uid] = (user, name, count, date)
    
    if user_id in user_limits:
        user, name, count, last_date = user_limits[user_id]
        if last_date == today:
            user_limits[user_id] = (user, name, count + 1, today)
        else:
            user_limits[user_id] = (user, name, 1, today)
    else:
        user_limits[user_id] = (username, full_name, 1, today)
    
    with open("user_limits.txt", "w") as f:
        for uid, (user, name, count, date) in user_limits.items():
            f.write(f"{uid} {user} {name} {count} {date}\n")

def download_instagram_video(url):
    try:
        L = instaloader.Instaloader()
        post = instaloader.Post.from_shortcode(L.context, url.split("/")[-2])
        if post.is_video:
            video_url = post.video_url
            response = requests.get(video_url)
            if response.status_code == 200:
                return response.content
        return None
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        return None

def save_to_file(user_info, user_id, url, success, request_number):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "✅ Muvaffaqiyatli" if success else "❌ Muvaffaqiyatsiz"
    log_message = f"👤 {user_info} (ID: {user_id}), 🔗 {url}, 📅 {timestamp}, ⛽ Status: {status}, #️⃣ Ariza: {request_number}"
    
    # Faylga yozish
    with open("baza.txt", "a", encoding='utf-8') as file:
        file.write(log_message + "\n")
    
    # Terminalga chiqarish
    print(log_message)




def log_activity(user, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_info = f"👤 {user.first_name or ''} {user.last_name or ''} @{user.username or 'Nomalum'} (ID: {user.id})"
    log_message = f"{timestamp} - {user_info}: {message}"

    # Logni faylga yozish
    with open("log.txt", "a", encoding='utf-8') as file:
        file.write(log_message + "\n")

    # Terminalga chiqarish
    print(log_message)


async def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    log_activity(user, "Start bosdi")  # Start bosganini logga yozish

    keyboard = [
        [InlineKeyboardButton("📊 Limitni ko'rish", callback_data='limit')],
        [InlineKeyboardButton("ℹ️ Biz haqimizda", callback_data='about')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Quyidagi tugmalardan birini tanlang:", reply_markup=reply_markup)

async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user = query.from_user
    user_id = user.id
    await query.answer()
    
    if query.data == "limit":
        used_limit, remaining_limit = check_user_limit(user_id, user.username, user.first_name, user.last_name)
        await query.message.reply_text(f"📊 Sizning bugungi foydalangan limitingiz: {used_limit}")
    elif query.data == "about":
        await query.message.reply_text("ℹ️ Biz haqimizda: Bu bot Instagram reels videolarini yuklab olish uchun yaratilgan.")

async def handle_message(update: Update, context: CallbackContext):
    user = update.message.from_user
    text = update.message.text
    log_activity(user, f"Yozdi: {text}")  # Foydalanuvchi yozganini logga yozish

    if any(word in text.lower() for word in ["salom", "assalom", "salomm"]):
        await update.message.reply_text("Assalom alekom! 😊\nMenga Instagram havola yuboring men sizga Video qilib yuboraman!")
        return
    elif any(word in text.lower() for word in ["rahmat", "raxmat", " "]):
        await update.message.reply_text("Bizning xizmatlardan foydalanganingiz uchun tashakkur! 😊")
        return
    elif any(word in text.lower() for word in ["qalesan", "qalisan", "qlesan","qaleysan"]):
        await update.message.reply_text("Yaxshi raxmat! 😊\nMenga Instagram havola yuboring men sizga Video qilib yuboraman!")
        return

    if "instagram.com" in text:
        used_limit, remaining_limit = check_user_limit(user.id, user.username, user.first_name, user.last_name)
        if used_limit >= DAILY_LIMIT:
            await update.message.reply_text(f"❌ Sizning bugungi xizmat limingiz tugadi. \nLimitlar {used_limit}/{DAILY_LIMIT}")
            return
        
        request_number = get_next_request_number()
        if request_number is None:
            await update.message.reply_text("❌ Umumiy xizmat limiti tugagan.")
            return

        await update.message.reply_text("⏳ Video yuklanmoqda... Iltimos, biroz kuting.")
        video_content = download_instagram_video(text)
        if video_content:
            increment_user_limit(user.id, user.username, user.first_name, user.last_name)
            await update.message.reply_video(video=video_content, caption=f"🔗 Havola: {text}\n#️⃣ Ariza raqami: {request_number}\nSizning qolgan kunlik limitingiz: {remaining_limit - 1}/{DAILY_LIMIT}")
            save_to_file(f"{user.first_name or ''} {user.last_name or ''} @{user.username or 'NoUsername'}", user.id, text, True, request_number)
        else:
            save_to_file(f"{user.first_name or ''} {user.last_name or ''} @{user.username or 'NoUsername'}", user.id, text, False, request_number)
            await update.message.reply_text(f"❌ Video yuklab olishda xatolik.\n#️⃣ Ariza raqami: {request_number}")
    else:
        await update.message.reply_text(f"❌ Iltimos, faqat Instagram video havolasini yuboring.")

def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()
    



if __name__ == '__main__':
    main()