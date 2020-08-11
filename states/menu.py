from aiogram.dispatcher.filters.state import StatesGroup, State

class Menu(StatesGroup):
    get_profile_url = State()
    main_menu = State()
    get_coefs = State()