import asyncio
import logging

from aiogram import Dispatcher
from aiogram.types import BotCommand

from bot import bot
from scheduler import scheduler
from database.database import create_database

from handlers.start import router as start_router
from handlers.reminders import router as reminders_router

logging.basicConfig(level=logging.INFO)

dp = Dispatcher()

dp.include_router(start_router)
dp.include_router(reminders_router)


async def main():
    create_database()     #создание базы
    scheduler.start()     #запуск планировщика
    await bot.set_my_commands([                          #добавление команды /start в меню бота
        BotCommand(
            command="start",
            description="Главное меню"
        )
    ])
    await dp.start_polling(bot  ) #запуск бота и ожидание новых сообщений, говорим боту,следи задейтсвиями если их нет,жди


if __name__ == "__main__":#"Если этот файл оказался главным (потому чтопользователь егозапустил),тогда выполни код ниже"
    asyncio.run(main())