import subprocess
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import asyncio

API_TOKEN = '7785195597:AAFhB2PhIQH6kcpo1NBQCkuADE8phYrMcO8'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

user_data = {}


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет!\nЯ бот, который может узнать прогноз погоды на ближайшие 7 дней в любых городах. Буду рад помочь!\n"
        "Используйте команду /weather, чтобы начать."
    )


@dp.message(Command("help"))
async def answer(message: types.Message):
    await message.answer(
        "У меня есть единственная команда:\n/weather - узнать погоду в начальном и конечном городе за следующие 7 дней"
    )


@dp.message(Command("weather"))
async def cmd_weather(message: types.Message):
    await message.answer("Введите начальный город(строго на английском):")
    user_data[message.from_user.id] = {'start_city': None, 'end_city': None, 'days': None}


@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        return
    user_info = user_data[user_id]
    if user_info['start_city'] is None:
        user_info['start_city'] = message.text
        await message.answer("Введите конечный город(строго на английском):")
        return
    if user_info['end_city'] is None:
        user_info['end_city'] = message.text
        await ask_days(user_id)
        return
    days_map = {
        "1 день": "1",
        "2 дня": "2",
        "3 дня": "3",
        "4 дня": "4",
        "5 дней": "5",
        "6 дней": "6",
        "7 дней": "7"
    }

    if message.text in days_map:
        user_info['days'] = days_map[message.text]
        start_city = user_info['start_city']
        end_city = user_info['end_city']
        url = f"http://127.0.0.1:8050/dash/?start_city={start_city}&end_city={end_city}&days={user_info['days']}"

        await bot.send_message(user_id,
                               f"Вы выбрали:\nНачальный город: {start_city}\nКонечный город: {end_city}\nКоличество дней: {user_info['days']}\n"
                               f"Вы можете просмотреть прогноз погоды по следующей ссылке(не забудьте нажать кнопочку <посмотрерть секретики>): {url}")
        subprocess.Popen(['python', 'app.py'])
        del user_data[user_id]
    else:
        await message.answer("Пожалуйста, выберите количество дней из предложенных вариантов.")


async def ask_days(user_id: int):
    kb = [
        [
            types.KeyboardButton(text="1 день"),
            types.KeyboardButton(text="2 дня"),
            types.KeyboardButton(text="3 дня"),
            types.KeyboardButton(text="4 дня"),
            types.KeyboardButton(text="5 дней"),
            types.KeyboardButton(text="6 дней"),
            types.KeyboardButton(text="7 дней"),
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите количество дней"
    )

    await bot.send_message(user_id, "Выберите количество дней для прогноза:", reply_markup=keyboard)
async def main():
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())
