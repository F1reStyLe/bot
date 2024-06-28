from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Календарь', callback_data="Calendar")]
])

crud = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Добавить', callback_data="cal_add"),
        InlineKeyboardButton(text='Удалить', callback_data="cal_del"),
        InlineKeyboardButton(text='Удалить всё', callback_data="del_all"),
    ]
])

yes_no = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Да', callback_data="yes"),
        InlineKeyboardButton(text='Нет', callback_data="no"),
    ]
])