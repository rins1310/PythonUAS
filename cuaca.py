from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ConversationHandler
)
import requests
import logging
from datetime import datetime

# Konfigurasi Token dan API
TELEGRAM_BOT_TOKEN = "7675147578:AAHFvbYyKIV74vqGWsu13_L68Tp5Ixfnano"
OPENWEATHERMAP_API_KEY = "a3d15709324f10f26a75b3967c00b2ae"

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# State untuk ConversationHandler
CUACA_STATE = 1
RAMALAN_STATE = 2

# Variabel Global
monitored_city = None

# Fungsi Mendapatkan Cuaca Saat Ini
def get_current_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric&lang=id"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather = data["weather"][0]["description"].capitalize()
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        return (
            f"🌤️ *Cuaca Saat Ini di {city.capitalize()}* 🌤️\n"
            f"🌡️ Suhu: {temp}°C\n"
            f"💧 Kelembapan: {humidity}%\n"
            f"🍃 Kecepatan Angin: {wind_speed} m/s\n"
            f"🌥️ Kondisi: {weather}"
        )
    else:
        return "⚠️ Kota tidak ditemukan. Pastikan nama kota benar."

# Fungsi Mendapatkan Ramalan Cuaca
def get_weather_forecast(city):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric&lang=id"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        forecasts = ["📅 *Ramalan Cuaca:*"]
        for forecast in data["list"][:5]:
            time = datetime.fromtimestamp(forecast["dt"]).strftime("%d-%m %H:%M")
            weather = forecast["weather"][0]["description"].capitalize()
            temp = forecast["main"]["temp"]
            forecasts.append(f"🕒 {time} | 🌡️ {temp}°C | 🌥️ {weather}")
        return "\n".join(forecasts)
    else:
        return "⚠️ Kota tidak ditemukan. Pastikan nama kota benar."

# Handler untuk /start
async def start(update, context):
    await update.message.reply_text(
        "Selamat datang di Bot Pemantau Cuaca!\n\n"
        "Gunakan perintah berikut:\n"
        "/CuacaTerkini - Lihat cuaca saat ini\n"
        "/RamalanCuaca - Lihat ramalan cuaca\n",
        parse_mode="Markdown"
    )

# Handler untuk /CuacaTerkini
async def cuaca_terkini_start(update, context):
    await update.message.reply_text("Harap masukkan nama kota:")
    return CUACA_STATE

async def cuaca_terkini_provide(update, context):
    city = update.message.text
    weather_info = get_current_weather(city)
    await update.message.reply_text(weather_info, parse_mode="Markdown")
    return ConversationHandler.END

# Handler untuk /RamalanCuaca
async def ramalan_cuaca_start(update, context):
    await update.message.reply_text("Harap masukkan nama kota:")
    return RAMALAN_STATE

async def ramalan_cuaca_provide(update, context):
    city = update.message.text
    forecast_info = get_weather_forecast(city)
    await update.message.reply_text(forecast_info, parse_mode="Markdown")
    return ConversationHandler.END


# Fungsi Utama
def main():
    # Inisialisasi Bot
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # ConversationHandler untuk masing-masing perintah
    cuaca_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("CuacaTerkini", cuaca_terkini_start)],
        states={CUACA_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, cuaca_terkini_provide)]},
        fallbacks=[],
    )

    ramalan_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("RamalanCuaca", ramalan_cuaca_start)],
        states={RAMALAN_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ramalan_cuaca_provide)]},
        fallbacks=[],
    )
    # Tambahkan Handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(cuaca_conv_handler)
    application.add_handler(ramalan_conv_handler)
    # Jalankan Bot
    application.run_polling()

if __name__ == "__main__":
    main()
