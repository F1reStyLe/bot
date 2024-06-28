from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Календарь', callback_data="Calendar")]
])