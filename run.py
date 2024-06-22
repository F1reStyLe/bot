import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import Config

bot = Bot(token=Config.token)
dp = Dispatcher()

@dp.message(CommandStart)
async def cmd_start(message: Message):
    await message.answer('Hello')


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    if Config.debug:
        logging.basicConfig(level=logging.INFO)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')