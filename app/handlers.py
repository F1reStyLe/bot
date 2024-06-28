from datetime import datetime

from aiogram import F, Router

from aiogram.filters import CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery
from aiogram_calendar import SimpleCalendarCallback, get_user_locale

import app.keyboards as kb

from .custom_calendar import CustomCalendar

router = Router()

@router.message(CommandStart)
async def cmd_start(message: Message):
    await message.answer('Hello', reply_markup=kb.settings)


today = datetime.now()

@router.callback_query(F.data == "Calendar")
async def nav_cal_handler_date(callback_query: CallbackQuery):
    calendar = CustomCalendar(
        locale=await get_user_locale(callback_query.from_user), show_alerts=True
    )
    calendar.set_dates_range(datetime(today.year - 3, 1, 1), datetime(today.year + 3, 12, 31))
    await callback_query.message.answer(
        "Выберите дату: ",
        reply_markup=await calendar.start_calendar(year=today.year, month=today.month)
    )

@router.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: CallbackData):
    calendar = CustomCalendar(
        locale=await get_user_locale(callback_query.from_user), show_alerts=True
    )
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2025, 12, 31))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(
            f'{date.strftime("%d/%m/%Y")}'
        )