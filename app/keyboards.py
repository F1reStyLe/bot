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

create = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Добавить', callback_data="cal_add")
    ]
])

yes_no = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Да', callback_data="yes"),
        InlineKeyboardButton(text='Нет', callback_data="no"),
    ]
])

def kb_builder(_items):
    keyboard = []

    for item in sorted(_items, key = lambda x: x[3]):
        keyboard.append([InlineKeyboardButton(text=f'{item[1]} {item[3]:%H:%M}', callback_data=str(item[0]))])

    builder = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return builder
