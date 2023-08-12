import logging
from aiogram import Dispatcher

from data.config import admins


async def notify_admin(dp: Dispatcher, message):
    for admin in admins:
        try:
            await dp.bot.send_message(admin, message)
        except Exception as err:
            logging.exception(err)
