from datetime import datetime

from aiogram import F, Router

from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery
from aiogram_calendar import SimpleCalendarCallback, get_user_locale
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from .custom_calendar import CustomCalendar
import app.keyboards as kb
from db.db import DBConnect

from config import Config

router = Router()

calendar_data = None

db = DBConnect(database=Config.database, user=Config.user,
                password=Config.password, host=Config.host)
today = datetime.now()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer('Привет! Я помогу тебе запланировать твою неделю. Выбери дату:', reply_markup=kb.settings)

@router.message(Command("calendar"))
async def cmd_calendar(message: Message):
    await message.answer('Выбери дату:', reply_markup=kb.settings)

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
        global calendar_data
        calendar_data = date
        if len(routine) > 0:
            await callback_query.message.answer(
                f'Планы на {date.strftime("%d/%m/%Y")}: \n {"\n".join(i[1] for i in routine)}',
                reply_markup=kb.crud
            )
        else:
            await callback_query.message.answer("Планы отсутствуют", reply_markup=kb.create)

@router.callback_query(F.data == "cal_add")
async def process_add_note(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state("add_note")
    await callback_query.message.answer("Что необходимо добавить?")

@router.message(StateFilter("add_note"))
async def add_note(message: Message, state: FSMContext):
    to_do_list = await state.get_data()
    if to_do_list.get("notes") is None:
        to_do_list["notes"] = []

    to_do_list["notes"].append(message.text)
    await state.set_data(to_do_list)

    await state.set_state("next_add")
    await message.answer("Добавим что- то ещё?", reply_markup=kb.yes_no)

@router.callback_query(StateFilter("next_add"), F.data == "yes")
async def process_add_next(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state("add_note")
    await callback_query.message.answer("Что необходимо добавить?")

@router.callback_query(StateFilter("next_add"), F.data == "no")
async def process_add_next(callback_query: CallbackQuery, state: FSMContext):
    to_do_list = await state.get_data()
    if calendar_data:
        await state.set_state("insert_db")
        await callback_query.message.answer(f"Хорошо, это все что нужно добавить на \
{calendar_data.strftime('%d/%m/%Y')}?\n {"\n".join(to_do_list["notes"])}",
            reply_markup=kb.yes_no)
    else:
        await state.clear()
        await callback_query.message.answer(f"Вы пытаетесь добавить запись не выбрав дату...",
                                            reply_markup=kb.settings)

@router.callback_query(StateFilter("insert_db"), F.data == "yes")
async def process_insert_db(callback_query: CallbackQuery, state: FSMContext):
    to_do_list = await state.get_data()
    await add_to_routine(db, calendar_data, to_do_list["notes"])
    await state.clear()
    await callback_query.message.answer("Готово!")

@router.callback_query(StateFilter("insert_db"), F.data == "no")
async def process_insert_db(callback_query: CallbackQuery, state: FSMContext):
    F.data = "yes"
    await state.set_state("add_note")

@router.callback_query(F.data == "cal_del")
async def process_del_note(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state("del_note")
    items = await process_get_routine(calendar_data)
    await callback_query.message.answer("Какую запись необходимо удалить?", reply_markup=kb.kb_builder(items))

@router.callback_query(StateFilter("del_note"))
async def add_note(callback_query: Message, state: FSMContext):
    await del_routine(db, callback_query.data)
    await state.clear()
    await callback_query.message.answer("Запись удалена!")

@router.callback_query(F.data == "del_all")
async def process_del_all(callback_query: CallbackQuery, state: FSMContext):
    if calendar_data:
        await del_all_routine(calendar_data)
        await callback_query.message.answer("Все записи удалены!")
    else:
        await callback_query.message.answer(f"Вы пытаетесь удалить записи не выбрав дату...",
                                        reply_markup=kb.settings)

async def process_get_routine(_date):
    # Connect to the database
    _conn = await db.connect()

    # Initialize the routine string
    _routine = []

    # Execute a SQL query to fetch the routine for the given date
    async with _conn.transaction():
        async for desc in _conn.cursor('''
            select row_id, description
            from "routine"
            where event_date = $1::date
            ''', _date):
            # Append the description to the routine string, separated by a newline
            _routine.append((desc["row_id"], desc["description"]))

    # Return the routine for the given date
    return _routine

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

async def add_to_routine(_db, _date, _descriptions):
    _conn = await _db.connect()
    async with _conn.transaction():
        for description in _descriptions:
            await _conn.execute('''
                insert into "routine" (event_date, description)
                values ($1::date, $2)
                ''', _date, description)

async def del_routine(_db, _row_id):
    _conn = await _db.connect()
    async with _conn.transaction():
        await _conn.execute('''
            delete from "routine"
            where row_id = $1
            ''', int(_row_id))

async def del_all_routine(_date):
    _conn = await db.connect()
    async with _conn.transaction():
        await _conn.execute('''
            delete from "routine"
            where event_date = $1
            ''', _date)
