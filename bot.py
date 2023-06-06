from aiogram import Bot, Dispatcher, types
from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyowm import OWM
import sqlite3

TOKEN = ''
owm = OWM('')
bot = Bot(TOKEN)
dp = Dispatcher(bot)
gender_cb = CallbackData("gender", "answer")

# Создание базы данных для хранения пола пользователей
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (user_id INT, gender TEXT)')

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

    c.execute('INSERT INTO users VALUES (?, ?)', (user_id, gender))
    conn.commit()

    await call.message.reply("Спасибо! Теперь вы можете использовать команду /weather для получения прогноза погоды и рекомендаций по одежде.")

# Команда для получения прогноза погоды
@dp.message_handler(commands=['weather'])
async def weather_command(message: types.Message):
    await message.reply("Введите город:")

    if __name__ == '__main__':
        from aiogram import executor
        executor.start_polling(dp)
