from aiogram import Bot, Dispatcher, types
from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyowm import OWM
import sqlite3

TOKEN = ''
owm = OWM('')
mgr = owm.weather_manager()
bot = Bot(TOKEN)
dp = Dispatcher(bot)
gender_cb = CallbackData("gender", "answer")
day_cb = CallbackData("day", "day_number")

# Создание базы данных для хранения пола пользователей
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (user_id INT, gender TEXT, city TEXT)')

def get_clothes_recommendation(temp: float, gender: str):
    # Рекомендация одежды в зависимости от температуры и пола
    pass  # Заполните эту функцию

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Мужчина", callback_data=gender_cb.new(answer="male")),
                 InlineKeyboardButton("Женщина", callback_data=gender_cb.new(answer="female")))
    await message.reply("Пожалуйста, выберите ваш пол:", reply_markup=keyboard)

@dp.callback_query_handler(gender_cb.filter())
async def query_handler(call: types.CallbackQuery, callback_data: dict):
    gender = callback_data.get("answer")
    user_id = call.from_user.id
    c.execute('INSERT INTO users VALUES (?, ?, ?)', (user_id, gender, None))
    conn.commit()
    await call.message.reply("Спасибо! Теперь, пожалуйста, введите город, в котором вы живете.")

@dp.message_handler()
async def get_city(message: types.Message):
    user_id = message.from_user.id
    city = message.text
    c.execute('UPDATE users SET city = ? WHERE user_id = ?', (city, user_id))
    conn.commit()
    await message.reply("Спасибо! Теперь вы можете использовать команду /weather для получения прогноза погоды и рекомендаций по одежде.")

@dp.message_handler(commands=['weather'])
async def weather_command(message: types.Message):
    user_id = message.from_user.id
    c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = c.fetchone()
    if user is None:
        await message.reply("Пожалуйста, сначала введите ваш пол и город.")
        return
    gender, city = user[1], user[2]
    weather = mgr.weather_at_place(city).weather
    temp = weather.temperature('celsius')["temp"]
    wind_speed = weather.wind()["speed"]
    precipitation = weather.rain if weather.rain else weather.snow
    clothes_recommendation = get_clothes_recommendation(temp, gender)
    message_text = f"Погода в городе {city} на сегодня:\n" \
                   f"Температура: {temp}°C\n" \
                   f"Скорость ветра: {wind_speed} м/с\n" \
                   f"Осадки: {precipitation}\n\n" \
                   f"Рекомендация по одежде: {clothes_recommendation}"

    await message.reply(message_text)


@dp.callback_query_handler(day_cb.filter())
async def query_handler(call: types.CallbackQuery, callback_data: dict):
    day_number = int(callback_data.get("day_number"))
    user_id = call.from_user.id

    c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = c.fetchone()
    if user is None:
        await call.message.reply("Пожалуйста, сначала введите ваш пол и город.")
        return

    gender, city = user[1], user[2]

    forecast = mgr.forecast_at_place(city, 'daily').forecast
    weather = forecast.get_weathers()[day_number]
    temp = weather.temperature('celsius')["day"]
    wind_speed = weather.wind()["speed"]
    precipitation = weather.rain if weather.rain else weather.snow

    clothes_recommendation = get_clothes_recommendation(temp, gender)

    message_text = f"Погода в городе {city} на {forecast.get_weathers()[day_number].reference_time('iso')}:\n" \
                   f"Температура: {temp}°C\n" \
                   f"Скорость ветра: {wind_speed} м/с\n" \
                   f"Осадки: {precipitation}\n\n" \
                   f"Рекомендация по одежде: {clothes_recommendation}"

    await call.message.edit_text(message_text)


if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp)

