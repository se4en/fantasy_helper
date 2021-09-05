from aiogram.dispatcher.filters.state import StatesGroup, State


class Check(StatesGroup):
    no_checking = State()
    checking_password = State()
    getting_profile = State()
    set_name = State()
    set_url = State()
    set_description = State()
