import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from themes import THEMES

TOKEN = "8271945254:AAFY79RsyOuKjBe4Jposj_NsarOD0pqpaxs"
URL_APP = "https://ggio.github.io/my-game-hub/" 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Глобальное состояние игры
game = {"players": [], "phase": "lobby", "theme": None, "day_count": 1}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    game["players"].clear()
    game["phase"] = "lobby"
    game["day_count"] = 1
    await message.answer("🎩 **MAFIA ONLINE LAB** 🎩\n\nНапиши /join для входа.")

@dp.message(Command("join"))
async def cmd_join(message: types.Message):
    if any(p['id'] == message.from_user.id for p in game["players"]):
        return await message.answer("Ты уже в игре!")
    game["players"].append({"id": message.from_user.id, "name": message.from_user.first_name, "is_bot": False, "status": "alive"})
    builder = InlineKeyboardBuilder()
    builder.button(text="🤖 Добавить ботов и НАЧАТЬ", callback_data="start_full_game")
    await message.answer(f"✅ Ты в лобби ({len(game['players'])}/6)", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "start_full_game")
async def start_full_game(callback: types.Callback_query):
    bot_names = ["Робот Вася", "Кибер-Петр", "Андроид Ева", "R2-D2", "Терминатор", "Валл-И"]
    while len(game["players"]) < 6:
        name = random.choice(bot_names)
        game["players"].append({"id": random.randint(1000, 9999), "name": name, "is_bot": True, "status": "alive"})
        bot_names.remove(name)
    builder = InlineKeyboardBuilder()
    for key in THEMES.keys():
        builder.button(text=THEMES[key]['name'], callback_data=f"theme_sel_{key}")
    await callback.message.answer("Выберите вселенную игры:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("theme_sel_"))
async def setup_roles(callback: types.Callback_query):
    theme_key = callback.data.split("_")[2]
    game["theme"] = THEMES[theme_key]
    roles = ["mafia", "doctor", "detective", "civilian", "civilian", "civilian"]
    random.shuffle(roles)
    random.shuffle(game["players"])

    for i, p in enumerate(game["players"]):
        p['role_key'] = roles[i]
        p['role_name'] = game["theme"]["roles"][p['role_key']]
        p['avatar'] = random.choice(game["theme"]["avatars"])
        if not p['is_bot']:
            link = f"{URL_APP}?role={p['role_name']}&avatar={p['avatar']}&name={p['name']}&role_key={p['role_key']}"
            kb = ReplyKeyboardBuilder()
            kb.row(types.KeyboardButton(text="📱 ТВОЯ КАРТА И ДЕЙСТВИЯ", web_app=WebAppInfo(url=link)))
            await bot.send_message(p['id'], f"🌑 ИГРА НАЧАЛАСЬ!\n\nТвоя роль: {p['role_name']}", reply_markup=kb.as_markup(resize_keyboard=True))

    await callback.message.answer(f"🌌 Мир: {game['theme']['name']}\nРоли распределены. Наступает НОЧЬ...")
    await start_night()

async def start_night():
    game["phase"] = "night"
    alive_players = [p for p in game["players"] if p['status'] == "alive"]
    await bot.send_message(game["players"][0]['id'], f"🌙 **НОЧЬ {game['day_count']}**. Сделай ход в Mini App!")

@dp.message(F.web_app_data)
async def handle_action(message: types.Message):
    if game["phase"] == "over": return

    # Логика НОЧИ
    if game["phase"] == "night":
        living_targets = [p for p in game["players"] if p['status'] == "alive" and p['id'] != message.from_user.id]
        target = random.choice(living_targets)
        target['status'] = "dead"
        await message.answer(f"☀️ **УТРО**. Этой ночью погиб: {target['avatar']} {target['name']}")
        if await check_victory(message): return
        
        game["phase"] = "day"
        await message.answer("🗣 **ДЕНЬ**. Время голосования! Кто мафия? Выбери в Mini App.")

    # Логика ДНЯ
    elif game["phase"] == "day":
        living_targets = [p for p in game["players"] if p['status'] == "alive" and p['id'] != message.from_user.id]
        target = random.choice(living_targets)
        target['status'] = "dead"
        await message.answer(f"⚖️ **СУД**. Город решил казнить: {target['avatar']} {target['name']}\nЕго роль была: {target['role_name']}")
        
        if await check_victory(message): return
        
        game["day_count"] += 1
        await message.answer(f"🌑 Снова наступает ночь...")
        await start_night()

async def check_victory(message):
    mafia = [p for p in game["players"] if p['role_key'] == "mafia" and p['status'] == "alive"]
    civilians = [p for p in game["players"] if p['role_key'] != "mafia" and p['status'] == "alive"]
    
    if not mafia:
        await message.answer("🎉 **ПОБЕДА МИРНЫХ!** Вся мафия устранена.")
        game["phase"] = "over"
        return True
    elif len(mafia) >= len(civilians):
        await message.answer("💀 **ПОБЕДА МАФИИ!** Мирные жители не смогли сопротивляться.")
        game["phase"] = "over"
        return True
    return False

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())