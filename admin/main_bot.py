import asyncio

from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from keyboards import add_influencer

dp = Dispatcher()
token = "7397933043:AAFzC0pkb0pWgkXQs-O80mlWenqQwoFBb2Q"

@dp.message(lambda message: message.text == "/start")
async def trade_handler(message: Message):
    influencer_button = add_influencer("AddInfluencer")
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[[influencer_button]])  # Передаем список списков
    await message.answer("Выберите опцию:", reply_markup=inline_kb)


async def main():
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())