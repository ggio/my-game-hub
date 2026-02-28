import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

# Пытаемся импортировать темы
try:
    from themes import THEMES
except ImportError:
    print("ОШИБКА: Файл themes.py не найден в этой папке!")
    THEMES = {}

TOKEN = "8271945254:AAFY79RsyOuKjBe4Jposj_NsarOD0pqpaxs"
URL_APP = "https://PRODESK.github.io/my-game-hub/" 

# Включаем логирование (чтобы видеть ошибки в терминале)
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

lobby = [] 
bot_names = ["Робот Вася", "Кибер-Петр", "Андроид Ева", "R2-D2", "Терминатор"]

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("🕵️‍♂️ Мафия онлайн.\nНапиши /join для входа в лобби.")

@dp.message(Command("join"))
async def cmd_join(message: types.Message):
    if any(p['id'] == message.from_user.id for p in lobby):
        await message.answer("Ты уже в очереди!")
        return
    lobby.append({"id": message.from_user.id, "name": message.from_user.first_name, "is_bot": False})
    builder = InlineKeyboardBuilder()
    builder.button(text="🤖 Добавить ботов и начать", callback_data="start_with_bots")
    await message.answer(f"✅ Ты в лобби! (Игроков: {len(lobby)}/6)", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "start_with_bots")
async def fill_with_bots(callback: types.Callback_query):
    game_players = list(lobby)
    needed = 6 - len(game_players)
    random_bots = random.sample(bot_names, needed)
    for name in random_bots:
        game_players.append({"id": random.randint(1000, 9999), "name": name, "is_bot": True})
    
    builder = InlineKeyboardBuilder()
    for key in THEMES.keys():
        builder.button(text=THEMES[key]['name'], callback_data=f"game_theme_{key}_{random.randint(1,100)}")
    await callback.message.answer("Выбери вселенную игры:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("game_theme_"))
async def setup_game(callback: types.Callback_query):
    await callback.answer()
    await callback.message.answer("🎮 Раздаю роли и готовлю игру...")

async def main():
    try:
        print("--- БОТ ЗАПУСКАЕТСЯ... ---")
        await dp.start_polling(bot)
    except Exception as e:
        print(f"ПРОИЗОШЛА ОШИБКА: {e}")

if __name__ == "__main__":
    asyncio.run(main())