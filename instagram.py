import os
import requests
import instaloader
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext
from datetime import datetime
from telegram.constants import ChatMemberStatus

# Bot tokenini shu yerga yozing
TOKEN = '6849473588:AAHKCSjNPD_Po7D86lDnw9nDlvbJyt7mQPs'

# Foydalanuvchi xizmat sanog'ini saqlash
USER_LIMIT = 1_000_000  # Umumiy foydalanuvchi limiti
DAILY_LIMIT = 15  # Kunlik limit

# Fayllarni yaratish (agar mavjud bo'lmasa)
if not os.path.exists("counter.txt"):
    with open("counter.txt", "w") as f:
        f.write("0")  # So'rovlar sonini saqlash uchun

if not os.path.exists("user_limits.txt"):
    with open("user_limits.txt", "w") as f:
        f.write("")  # Foydalanuvchi limitlarini saqlash uchun

# Kanal username
CHANNEL_USERNAME = "@IT_Creative_News"

# 🔍 Foydalanuvchi kanalga a'zo ekanligini tekshirish
async def is_user_subscribed(user_id, context):
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False  # Xatolik bo'lsa, foydalanuvchi a'zo emas deb qabul qilamiz

# 🚀 START komandasi
async def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id

    # Foydalanuvchi kanalga a'zo ekanligini tekshirish
    is_subscribed = await is_user_subscribed(user_id, context)

    if not is_subscribed:
        # Agar a'zo bo'lmagan bo'lsa, obuna bo'lish tugmasini yuboramiz
        keyboard = [
            [InlineKeyboardButton("📢 Kanalga obuna bo'lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton("✅ Obuna bo‘ldim", callback_data='check_subscription')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "⚠️ Botdan foydalanish uchun avval kanalimizga obuna bo‘ling!\n"
            "✅ Obuna bo‘lgandan keyin *“Obuna bo‘ldim”* tugmasini bosing!",
            reply_markup=reply_markup,
            parse_mode="MarkdownV2"
        )
    else:
        # Agar a'zo bo'lsa, asosiy menyuni ko'rsatamiz
        await show_main_menu(update.message, user)

# 📌 OBUNA TEKSHIRISH tugmasi bosilganda
async def check_subscription(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id

    # Foydalanuvchi kanalga a'zo ekanligini tekshirish
    is_subscribed = await is_user_subscribed(user_id, context)

    if not is_subscribed:
        await query.answer("🚫 Siz hali kanalga obuna bo‘lmadingiz!", show_alert=True)
    else:
        await query.answer("✅ Rahmat! Botdan foydalanishingiz mumkin.", show_alert=True)
        await show_main_menu(query.message, query.from_user)

# 📜 Asosiy menyuni ko‘rsatish
async def show_main_menu(message, user):
    keyboard = [
        [InlineKeyboardButton("📊 Limitni ko'rish", callback_data='limit')],
        [InlineKeyboardButton("ℹ️ Biz haqimizda", callback_data='about')],
        [InlineKeyboardButton("🤖 Bot statistikasi", callback_data='statistika')],
        [InlineKeyboardButton("👤 Admin bilan bog'lanish", callback_data='admin')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await message.reply_text(
        f"*Assalomu alaykum va rohmatullohi va barokatuh\\!* 🌿\n"
        f"👤 *Hurmatli {user.first_name}*, Botimizga Xush kelibsiz\\!👋 \n"
        f"🆔 *Raqamingiz:* `{user.id}`\n"
        f"🤖 *Bot yaratuvchisi:* [Husanbek Coder](https://husanbek\\-coder.uz)\n"
        f"📹 *YouTube sahifamizga obuna bo'ling:* [📺 YouTube kanali](https://www.youtube.com/@it\\_creative)\n"
        f"♻️ *Botni qayta ishga tushurish uchun* /start *ni bosing:*",
        reply_markup=reply_markup,
        parse_mode="MarkdownV2"
    )

# 📥 Foydalanuvchi xabarlarini qayta ishlash
async def handle_message(update: Update, context: CallbackContext):
    user = update.message.from_user
    text = update.message.text

    # Foydalanuvchi kanalga a'zo ekanligini tekshirish
    is_subscribed = await is_user_subscribed(user.id, context)

    if not is_subscribed:
        await update.message.reply_text("⚠️ Botdan foydalanish uchun avval kanalimizga obuna bo‘ling!")
        return

    # Matnli xabarlarni qayta ishlash
    if any(word in text.lower() for word in ["salom", "assalom", "salomm"]):
        await update.message.reply_text("Assalom alekom! 😊\nMenga Instagram havola yuboring men sizga Video qilib yuboraman!")
    elif any(word in text.lower() for word in ["rahmat", "raxmat"]):
        await update.message.reply_text("Bizning xizmatlardan foydalanganingiz uchun tashakkur! 😊")
    elif any(word in text.lower() for word in ["qalesan", "qalisan", "qlesan", "qaleysan"]):
        await update.message.reply_text("Yaxshi raxmat! 😊\nMenga Instagram havola yuboring men sizga Video qilib yuboraman!")
    elif any(word in text.lower() for word in ["💋"]):
        await update.message.reply_text("😊\nHis tuyg'ularga berilmang!\nHavola yuboring!")
    elif any(word in text.lower() for word in ["admin"]):
        await update.message.reply_text("Admin bilan bog'lanish uchun:\n@mBin_Dev_0039 telegram manzil\n+998 97 521 66 86 A'loqa raqami orqali\nBog'lanishingiz mumkin.\nBotni qayta ishga tushurish uchun /start")
    elif "instagram.com" in text:
        # Instagram havolasini qayta ishlash
        await process_instagram_url(update, context)
    else:
        await update.message.reply_text("❌ Iltimos, faqat Instagram video havolasini yuboring.\nBotni qayta ishga tushurish uchun /start")

# 📹 Instagram havolasini qayta ishlash
async def process_instagram_url(update: Update, context: CallbackContext):
    user = update.message.from_user
    text = update.message.text

    # Foydalanuvchi limitini tekshirish
    used_limit, remaining_limit = check_user_limit(user.id, user.username, user.first_name, user.last_name)
    if used_limit >= DAILY_LIMIT:
        await update.message.reply_text(f"❌ Sizning bugungi xizmat limingiz tugadi. \nLimitlar {used_limit}/{DAILY_LIMIT}\nBotni qayta ishga tushurish uchun /start")
        return

    # So'rov raqamini olish
    request_number = get_next_request_number()
    if request_number is None:
        await update.message.reply_text("❌ Umumiy xizmat limiti tugagan.\nBotni qayta ishga tushurish uchun /start")
        return

    # Video yuklash jarayoni
    await update.message.reply_text("⏳ Video yuklanmoqda... \nIltimos, biroz kuting.")
    video_content = download_instagram_video(text)
    if video_content:
        increment_user_limit(user.id, user.username, user.first_name, user.last_name)
        await update.message.reply_video(video=video_content, caption=f"🔗 Havola: {text}\n#️⃣ Ariza raqami: {request_number}\nSizning qolgan kunlik limitingiz: {remaining_limit - 1}/{DAILY_LIMIT}\nBotni qayta ishga tushurish uchun /start")
        save_to_file(f"{user.first_name or ''} {user.last_name or ''} @{user.username or 'Nomalum'}", user.id, text, True, request_number)
    else:
        save_to_file(f"{user.first_name or ''} {user.last_name or ''} @{user.username or 'Nomalum'}", user.id, text, False, request_number)
        await update.message.reply_text(f"❌ Video yuklab olishda xatolik.\n#️⃣ Ariza raqami: {request_number}")

# 📊 Statistika ko'rsatish
async def statistikani_korsat(update: Update, context: CallbackContext):
    total_users, total_requests, today_requests = get_statistics()
    statistikalar = (
        "📊 *Bot statistikasi* 📊\n\n"
        f"👤 Umumiy foydalanuvchilar: {total_users}\n"
        f"📥 Jami so‘rovlar: {total_requests}\n"
        f"📅 Bugungi so‘rovlar: {today_requests}\n"
    )
    await update.callback_query.message.reply_text(statistikalar, parse_mode="Markdown")

# 🚀 Botni ishga tushirish
def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    main()