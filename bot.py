import asyncio
from aiogram import Bot, types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyowm import OWM
from pyowm.utils import config
from pyowm.utils import timestamps

# tokens
TG_TOKEN = ''
OWM_TOKEN = ''

# users dict , ДА ЭТО ОБЫЧНЫЙ СЛОВАРЬ А НЕ БД :) , после каждого ребута данные пользователей будут слетать.
user_data = {}

# init bot
bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot)

# init owm
owm = OWM(OWM_TOKEN)
mgr = owm.weather_manager()

# keyboard for weather map
weather_keyboard = InlineKeyboardMarkup(row_width=2)
weather_keyboard.insert(InlineKeyboardButton("Сегодня", callback_data="today"))
weather_keyboard.insert(InlineKeyboardButton("Завтра", callback_data="tomorrow"))
weather_keyboard.insert(InlineKeyboardButton("Поменять город", callback_data="change_city"))

async def send_weather(city, chat_id, day="today"):
    try:
        if day == "today":
            observation = mgr.weather_at_place(city)
            weather = observation.weather
        else:
            forecast = mgr.forecast_at_place(city, 'daily')
            weather = forecast.get_weathers()[1]  # прогноз на завтра

        temp = weather.temperature('celsius')["temp"]
        wind_speed = weather.wind()["speed"]
        status = weather.status

        await bot.send_message(
            chat_id,
            f"Погода в городе {city} на {day}:\n"
            f"Температура: {temp}°C\n"
            f"Скорость ветра: {wind_speed} м/с\n"
            f"Осадки: {status}",
            reply_markup=weather_keyboard
        )
    except Exception as e:
        await bot.send_message(
            chat_id,
            f"Произошла ошибка при получении погоды для города {city}. Проверьте правильность названия города.",
            reply_markup=weather_keyboard
        )

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    user_data[message.chat.id] = {}
    await bot.send_message(message.chat.id, 'Пожалуйста, введите ваш город(на английском).')

@dp.message_handler(commands=['city'])
async def city_command(message: types.Message):
    await bot.send_message(message.chat.id, 'Пожалуйста, введите новый город(на английском).')

@dp.message_handler()
async def set_city(message: types.Message):
    user_data[message.chat.id] = {'city': message.text}
    await bot.send_message(message.chat.id, 'Спасибо! Теперь вы можете использовать команду /weather для получения прогноза погоды.')

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
