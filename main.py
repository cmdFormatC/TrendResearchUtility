import requests
import json
import pandas as pd
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils.callback_data import CallbackData
import asyncio
from urllib.parse import quote
from dotenv import load_dotenv

#Загрузка env
load_dotenv()

bot_token = os.environ.get("BOT_TOKEN")
bot = Bot(token=bot_token)
url = 'https://mpstats.io/api/wb/get/category'

dp = Dispatcher(bot)
fetch_data_callback = CallbackData("fetch", "data")


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)

    fetch_button = types.InlineKeyboardButton('Выгрузка категорий', callback_data=fetch_data_callback.new(data="fetch"))
    keyboard_markup.add(fetch_button)

    await message.reply("Тыкни кнопку пидор", reply_markup=keyboard_markup)


@dp.callback_query_handler(fetch_data_callback.filter(data="fetch"))
async def process_callback_button1(callback_query: types.CallbackQuery):
    await callback_query.answer()
    startRow = 0
    endRow = 5000
    df_list = []
    while True:
        headers = {
            'X-Mpstats-TOKEN': os.environ.get("API_TOKEN"),
            'Content-Type': 'application/json'
        }
        payload = {
            'startRow': startRow,
            'endRow': endRow,
            'filterModel': {
                'sales': {
                    'filterType': 'number',
                    'type': 'greaterThan',
                    'filter': 100
            }},
            'sortModel': [
                {'colId': 'revenue', 'sort': 'desc'}
            ]
        }
        
        params = {
            'path': 'Спорт'
        }

        response = requests.post(url, headers=headers, params=params, json=payload)
        if response.status_code == 200:
            data = response.json()
            df_list.append(pd.json_normalize(data["data"]))
            print(len(data['data']))
            print(endRow)
            if len(data['data']) < 5000:  # break if fewer than 5000 rows returned
                break
            startRow += 5000
            endRow += 5000
        else:
            print(response.text)
            await bot.send_message(callback_query.from_user.id, f"Все обосралось {response.status_code}")
            break

    if df_list:  # if df_list is not empty
        df = pd.concat(df_list)  # concatenate all dataframes in df_list
        filename = "output.xlsx"
        df.to_excel(filename, index=False)
        with open(filename, "rb") as file:
            await bot.send_document(callback_query.from_user.id, file, caption="Ваши данные")
        os.remove(filename)
    await callback_query.answer()


if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)