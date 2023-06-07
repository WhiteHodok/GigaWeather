import asyncio
from aiogram import Bot, types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyowm import OWM
from pyowm.utils import config
from pyowm.utils import timestamps

# tokens
TG_TOKEN = ''
OWM_TOKEN = ''

# users dict , ДА ЭТО ОБЫЧНЫЙ СЛОВАРЬ А НЕ БД :) , после каждого ребута данные пользователей будут слетать. kekw
user_data = {}

# init bot
bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot)

# init owm
owm = OWM(OWM_TOKEN)
mgr = owm.weather_manager()

# keyboard for weather map
pass



@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    user_data[message.chat.id] = {}
    await bot.send_message(message.chat.id, 'Пожалуйста, введите ваш город(на английском).')

@dp.message_handler(commands=['city'])
async def city_command(message: types.Message):
    pass

@dp.message_handler()
async def set_city(message: types.Message):
    user_data[message.chat.id] = {'city': message.text}
    pass

@dp.message_handler(commands=['weather'])
async def weather_command(message: types.Message):
    city = user_data.get(message.chat.id, {}).get('city')
    if city:
        await send_weather(city, message.chat.id)
    else:
        await bot.send_message(message.chat.id, 'Пожалуйста, введите ваш город(на английском).')

@dp.callback_query_handler(lambda c: c.data in ["today", "tomorrow"])
async def process_callback_button1(callback_query: types.CallbackQuery):
    city = user_data.get(callback_query.message.chat.id, {}).get('city')
    if city:
        await send_weather(city, callback_query.message.chat.id, day=callback_query.data)
    else:
        await bot.send_message(callback_query.message.chat.id, 'Пожалуйста, введите ваш город(на английском).')

@dp.callback_query_handler(lambda c: c.data == "change_city")
async def process_callback_change_city(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.message.chat.id, 'Пожалуйста, введите новый город(на английском).')

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp)
