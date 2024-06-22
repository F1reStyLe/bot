import asyncio

from aiogram import Bot, Dispatcher

bot = Bot(token='123')
dp = Dispatcher()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())