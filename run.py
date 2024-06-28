import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import Config

from app.handlers import router
from app.menu import set_commands

bot = Bot(token=Config.token)
dp = Dispatcher()

async def main():
    await set_commands(bot)
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    if Config.debug:
        logging.basicConfig(level=logging.INFO)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')