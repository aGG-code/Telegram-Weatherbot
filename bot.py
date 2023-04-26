# -*- coding: utf-8 -*-
from config import weatherbot_token, open_weather_token
import requests
import datetime
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

reply_keyboard = [['/set_city', '/show_weather', "/help", "/close"]]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


async def start(update, context):
    user = update.effective_user
    await update.message.reply_html(
        f"Привет, {user.mention_html()}! Я погодный бот. С моей помощью ты сможешь узнать погоду в любом городе мира! "
        f"Чтобы разобраться, как я работаю, нажми на '/help'.\nУдачной работы со мной! :)",
        reply_markup=markup
    )


async def set_city(update, context):
    await update.message.reply_text(f"Пожалуйста, введите название своего города латиницей с маленькой буквы.")
    return 1


async def new_city(update, context):
    context.user_data['city'] = update.message.text
    await update.message.reply_text(f"Город изменен на {update.message.text}.")
    return ConversationHandler.END


async def show_weather(update, context):
    emoji_codes = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Облачно \U00002601",
        "Rain": "Дождь \U00002614",
        "Drizzle": "Дождь \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U0001F328",
        "Mist": "Туман \U0001F32B"
    }
    try:
        s = 'http://api.openweathermap.org/data/2.5/weather'
        rec_params = {
            "q": context.user_data['city'],
            "appid": open_weather_token,
            "units": 'metric'
        }
        response = requests.get(s, rec_params)
        data = response.json()

        city = data["name"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]

        sky = data["weather"][0]["main"]
        if sky in emoji_codes:
            wd = emoji_codes[sky]
        else:
            wd = "Посмотри сам! Никак не разберу, что там за погода..."

        pressure = data["main"]["pressure"]
        humidity = data["main"]["humidity"]
        temp_max = data["main"]["temp_max"]
        temp_min = data["main"]["temp_min"]
        wind_speed = data["wind"]["speed"]
        wind_gust = data["wind"]["gust"]

        sunrise_time = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_time = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        day_length = sunset_time - sunrise_time

        await update.message.reply_text(f"*** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} ***\n"
                                        f"\nПогода в городе: {city}\nТемпература: {temp}°C, "
                                        f"ощущается как {feels_like}°C.\n"
                                        f"За окном: {wd}\n"
                                        f"\nДавление: {pressure} мм.рт.ст.\n"
                                        f"Влажность: {humidity}%.\n"
                                        f"Ветер {wind_speed}м/с с порывами до {wind_gust}м/с.\n"
                                        f"\nДиапазон температур в этот день: {temp_min}-{temp_max}°C.\n"
                                        f"Время восхода: {sunrise_time.strftime('%H:%M')}.\n"
                                        f"Время заката: {sunset_time.strftime('%H:%M')}.\n"
                                        f"Продолжительность светового дня: {day_length}."
                                        f"\nХорошего дня! :)")
    except:
        await update.message.reply_text('Что-то не выходит. Пожалуйста, проверьте название города.')


async def help_command(update, context):
    await update.message.reply_text(f"Чтобы задать город, нажми на '/set_city'."
                                    f"Чтобы узнать погоду, нажми на '/show_weather'.")


async def close_keyboard(update, context):
    await update.message.reply_text(
        "Пока!",
        reply_markup=ReplyKeyboardRemove()
    )


def main():
    application = Application.builder().token(weatherbot_token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("show_weather", show_weather))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("close", close_keyboard))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('set_city', set_city)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, new_city)]
        },
        fallbacks=[]
    )
    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == '__main__':
    main()