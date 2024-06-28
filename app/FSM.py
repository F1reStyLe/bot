from aiogram.fsm.state import StatesGroup, State

class AddNote(StatesGroup):
    add_note = State()
    add_calendar = State()
    insert_db = State()