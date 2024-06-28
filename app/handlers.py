from datetime import datetime

from aiogram import F, Router

from aiogram.filters import CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery
from aiogram_calendar import SimpleCalendarCallback, get_user_locale

import app.keyboards as kb

from .custom_calendar import CustomCalendar
from db.db import DBConnect

from config import Config

router = Router()

db = DBConnect(database=Config.database, user=Config.user,
                password=Config.password, host=Config.host)

@router.message(CommandStart)
async def cmd_start(message: Message):
    await message.answer('Hello', reply_markup=kb.settings)


today = datetime.now()

@router.callback_query(F.data == "Calendar")
async def nav_cal_handler_date(callback_query: CallbackQuery):
    routine = await get_routine_dates(db)

    calendar = CustomCalendar(routine=routine,
        locale=await get_user_locale(callback_query.from_user), show_alerts=True
    )
    calendar.set_dates_range(datetime(today.year - 3, 1, 1), datetime(today.year + 3, 12, 31))
    await callback_query.message.answer(
        "Выберите дату: ",
        reply_markup=await calendar.start_calendar(year=today.year, month=today.month)
    )

@router.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: CallbackData):
    # Fetch the routine dates from the database
    routine = await get_routine_dates(db)

    # Create a custom calendar with the fetched routine
    calendar = CustomCalendar(routine=routine,
                             locale=await get_user_locale(callback_query.from_user),
                             show_alerts=True)

    # Set the dates range for the calendar
    calendar.set_dates_range(datetime(today.year - 3, 1, 1), datetime(today.year + 3, 12, 31))

    # Process the selection on the calendar
    selected, date = await calendar.process_selection(callback_query, callback_data)

    # If a date was selected, fetch the routine for that date and send it as a message
    if selected:
        routine = await process_get_routine(date)
        await callback_query.message.answer(
            f'Планы на {date.strftime("%d/%m/%Y")}: \n {routine}'
        )


async def process_get_routine(_date):
    # Connect to the database
    _conn = await db.connect()

    # Initialize the routine string
    _routine = ""

    # Execute a SQL query to fetch the routine for the given date
    async with _conn.transaction():
        async for desc in _conn.cursor('''
            select description
            from "routine"
            where event_date = $1::date
            ''', _date):
            # Append the description to the routine string, separated by a newline
            _routine += f'{desc["description"]}\n'

    # Return the routine for the given date
    return _routine if _routine != "" else "Планы отсутствуют"

async def get_routine_dates(_db):
    _conn = await _db.connect()
    _busy_days = await _conn.fetchrow('''select array_agg(extract(day from event_date)::text) days,
                                            array_agg(extract(months from event_date)::text) months,
                                            array_agg(extract(year from event_date)::text) years
                                        from "routine"''')

    _routine = {
        "days": set(_busy_days["days"]),   # Set of busy days
        "months": set(_busy_days["months"]),   # Set of busy months
        "years": set(_busy_days["years"]),   # Set of busy years
    }

    return _routine
