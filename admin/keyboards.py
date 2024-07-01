from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

def add_influencer(text: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data='some_callback_data')
