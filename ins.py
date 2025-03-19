import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.enums import ChatMemberStatus
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties

API_TOKEN = "6136222902:AAE64GMDrKYMzf2iFxZH092iWi449fbjPUk"
CHANNEL_ID = "@IT_Creative_News"  # Kanal username'ini yozing (masalan: @ITNewsUz)

session = AiohttpSession()
bot = Bot(token=API_TOKEN, session=session, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# Inline tugmalar yaratamiz
def get_start_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Kanalga a'zo bo'lish", url=f"https://t.me/{CHANNEL_ID[1:]}")],
        [InlineKeyboardButton(text="✅ A'zo bo'ldim", callback_data="check_subscription")]
    ])
    return keyboard

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Botdan foydalanish uchun kanalga a'zo bo'ling!", reply_markup=get_start_keyboard())

@dp.callback_query(lambda c: c.data == "check_subscription")
async def check_subscription(callback_query: types.CallbackQuery):
    user = callback_query.from_user.id
    chat_member = await bot.get_chat_member(CHANNEL_ID, user)

    if chat_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR]:  # "OWNER" olib tashlandi
        await callback_query.message.answer("✅ Assalomu alaykum! Botdan foydalanishingiz mumkin.")
    else:
        await callback_query.message.answer(
            "🚫 Siz hali kanalga a'zo bo'lmadingiz!\n\nIltimos, avval kanalga a'zo bo'ling.",
            reply_markup=get_start_keyboard()
        )

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
