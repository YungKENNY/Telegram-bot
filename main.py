import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from settings import settings
from aiogram.filters import Command
from aiogram import F
import database.models as models
from bs_orm.Requests import create_tables
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta


from handlers.basic import get_start, get_help, get_settings, get_schedule
from keyboards.callback import actual_settings, select_theme, select_group,\
select_time, group_was_selected, time_was_selected, theme_was_selected, close
from utils.commands import set_commands
from utils.parse import update_files
from utils.schedule import send_schedule


async def start_bot(bot: Bot):
    await set_commands(bot)
    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(admin_id, "Бот запущен!")
        except Exception as ex:
            print('Ошибка при попытке уведомить админов о включении бота:\n',
                  ex)


async def stop_bot(bot: Bot):
    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(admin_id, "Бот остановлен!")
        except Exception as ex:
            print(
                'Ошибка при попытке уведомить админов о выключении бота:\n',ex)


async def start():
    create_tables(models)

    bot = Bot(token=settings.bot_token)
    
    dp = Dispatcher()
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    scheduler.add_job(update_files, trigger='interval', minutes=60,
                      next_run_time=datetime.now()\
                        .replace(hour=14, minute=45, second=0, microsecond=0),
                      kwargs={'bot':bot})
    scheduler.add_job(send_schedule, trigger='interval', minutes=60,
                      next_run_time=datetime.now()\
                        .replace(hour=15, minute=0, second=0, microsecond=0),
                      kwargs={'bot':bot})
    scheduler.start()
    # await send_schedule(bot)
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)


    dp.message.register(get_start, Command(commands=['start', 'run']))
    dp.message.register(get_help, Command(commands=['help', 'h']))
    dp.message.register(get_settings, Command(commands=['settings']))
    dp.message.register(get_schedule, Command(commands=['send_schedule']))


    dp.callback_query.register(actual_settings, F.data=='actual_settings')
    dp.callback_query.register(select_theme, F.data=='select_theme')
    dp.callback_query.register(select_group, F.data=='select_group')
    dp.callback_query.register(select_time, F.data=='select_time')
    dp.callback_query.register(group_was_selected, 
                               F.data.startswith('group_was_selected'))
    dp.callback_query.register(time_was_selected, 
                               F.data.startswith('time_was_selected'))
    dp.callback_query.register(theme_was_selected, 
                               F.data.startswith('theme_was_selected'))
    dp.callback_query.register(close, F.data=='close')


    try:
        await dp.start_polling(bot)
    except Exception as ex: 
        print(f"ERROR:\n{ex}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(start())