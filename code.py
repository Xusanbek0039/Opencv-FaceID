import logging
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor

# Telegram bot tokeningizni shu yerga qo'ying
TOKEN = "YOUR_BOT_TOKEN"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Loglarni yoqish
logging.basicConfig(level=logging.INFO)

async def download_instagram_video(url):
    """Instagram video yuklovchi funksiya"""
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'instagram_video.mp4',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

@dp.message_handler(commands=['start'])
async def start(message: Message):
    await message.reply("👋 Assalomu alaykum!\n\nInstagramdan video yuklash uchun menga link yuboring.")

@dp.message_handler()
async def handle_instagram_link(message: Message):
    url = message.text

    if "instagram.com" in url:
        try:
            await message.reply("📥 Yuklanmoqda, biroz kuting...")
            
            # Videoni yuklash
            await download_instagram_video(url)
            
            # Yuklangan videoni foydalanuvchiga jo‘natish
            with open("instagram_video.mp4", "rb") as video:
                await message.reply_video(video)

        except Exception as e:
            await message.reply(f"❌ Xatolik yuz berdi: {str(e)}")
    else:
        await message.reply("❗ Iltimos, Instagram havolasini yuboring.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
