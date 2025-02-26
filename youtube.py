from aiogram import Bot, Dispatcher, types, F
import asyncio
import logging
import os
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytube import YouTube

TOKEN = "6849473588:AAEEt5wy0Mq3Dja3yJ--GXzRcavWqoev7_A"

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)



HTML_FILE = "index.html"

def save_to_html(username, full_name, link):
    """Foydalanuvchi ma'lumotlarini HTML faylga saqlaydi"""
    if not os.path.exists(HTML_FILE):
        with open(HTML_FILE, "w", encoding="utf-8") as file:
            file.write("""
            <html>
            <head><title>Saqlangan YouTube Havolalar</title></head>
            <body>
                <h2>Foydalanuvchilar yuborgan YouTube havolalar</h2>
                <table border='1' cellpadding='5' cellspacing='0'>
                    <tr>
                        <th>👤 Username</th>
                        <th>👥 Ism</th>
                        <th>🔗 Havola</th>
                    </tr>
            """)

    with open(HTML_FILE, "a", encoding="utf-8") as file:
        file.write(f"""
            <tr>
                <td>{username}</td>
                <td>{full_name}</td>
                <td><a href="{link}" target="_blank">{link}</a></td>
            </tr>
        """)

@dp.message(F.text == "/start")
async def start_command(message: types.Message):
    await message.answer("🎥 Salom! Menga YouTube havolani yuboring, men esa sizga videoni yuklab beraman.")

@dp.message(F.text.startswith("http"))
async def process_youtube_link(message: types.Message):
    url = message.text
    user = message.from_user.username or "No Username"
    full_name = message.from_user.full_name

    save_to_html(user, full_name, url)  # Ma'lumotlarni HTML faylga yozamiz

    try:
        yt = YouTube(url)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"📹 {stream.resolution}", callback_data=f"download_{stream.resolution}_{url}")]
            for stream in yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution")
        ])
        await message.answer(f"🎬 *{yt.title}* videosini qaysi formatda yuklamoqchisiz?", reply_markup=keyboard, parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"⚠ Xatolik yuz berdi: {str(e)}")

@dp.callback_query(F.data.startswith("download_"))
async def download_video(call: types.CallbackQuery):
    _, resolution, url = call.data.split("_")
    await call.message.edit_text(f"📥 Yuklanmoqda... {resolution}")

    try:
        yt = YouTube(url)
        video = yt.streams.filter(progressive=True, file_extension="mp4", resolution=resolution).first()
        file_path = video.download(DOWNLOAD_FOLDER)

        await bot.send_video(call.message.chat.id, open(file_path, "rb"), caption=f"🎥 {yt.title} ({resolution}) yuklandi!")
        os.remove(file_path)  # Faylni o‘chirib tashlaymiz
    except Exception as e:
        await call.message.edit_text(f"⚠ Yuklashda xatolik: {str(e)}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
