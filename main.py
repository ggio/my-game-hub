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

# Глобальные переменные игры
game = {
    "players": [],
    "phase": "lobby", # lobby, night, day
    "theme": None
}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    game["players"].clear()
    game["phase"] = "lobby"
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
    # Добираем ботов
    bot_names = ["Робот Вася", "Кибер-Петр", "Андроид Ева", "R2-D2", "Терминатор"]
    while len(game["players"]) < 6:
        game["players"].append({
            "id": random.randint(1000, 9999), 
            "name": random.choice(bot_names), 
            "is_bot": True, 
            "status": "alive"
        })
        bot_names.remove(game["players"][-1]["name"])

    builder = InlineKeyboardBuilder()
    for key in THEMES.keys():
        builder.button(text=THEMES[key]['name'], callback_data=f"theme_sel_{key}")
    await callback.message.answer("Выберите вселенную игры:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("theme_sel_"))
async def setup_roles(callback: types.Callback_query):
    theme_key = callback.data.split("_")[2]
    game["theme"] = THEMES[theme_key]
    
    # Раздача ролей
    roles = ["mafia", "doctor", "detective", "civilian", "civilian", "civilian"]
    random.shuffle(roles)
    random.shuffle(game["players"])

    for i, p in enumerate(game["players"]):
        p['role_key'] = roles[i]
        p['role_name'] = game["theme"]["roles"][p['role_key']]
        p['avatar'] = random.choice(game["theme"]["avatars"])
        if not p['is_bot']:
            # Персональная кнопка для игрока
            link = f"{URL_APP}?role={p['role_name']}&avatar={p['avatar']}&name={p['name']}&role_key={p['role_key']}"
            kb = ReplyKeyboardBuilder()
            kb.row(types.KeyboardButton(text="📱 ТВОЯ КАРТА И ДЕЙСТВИЯ", web_app=WebAppInfo(url=link)))
            await bot.send_message(p['id'], f"🌑 ИГРА НАЧАЛАСЬ!\n\nТвоя роль: {p['role_name']}", reply_markup=kb.as_markup(resize_keyboard=True))

    await callback.message.answer("🎭 Роли распределены! Город засыпает. Наступает НОЧЬ...")
    game["phase"] = "night"
    await asyncio.sleep(3)
    await run_night_phase(callback.message)

async def run_night_phase(message):
    await message.answer("🌙 **НОЧЬ**. Мафия, Шериф и Доктор делают свой выбор в Mini App...")
    # Боты делают ходы мгновенно
    # ... (логика ботов пропущена для простоты, они просто ждут тебя)

@dp.message(F.web_app_data)
async def handle_action(message: types.Message):
    action_data = message.web_app_data.data # Например "ACTION:kill"
    
    if game["phase"] == "night":
        # Упрощенная логика: кто-то из ботов умирает после твоего хода
        living_bots = [p for p in game["players"] if p['is_bot'] and p['status'] == "alive"]
        if not living_bots: return
        
        target = random.choice(living_bots)
        target['status'] = "dead"
        
        await message.answer(f"☀️ **УТРО**. Город просыпается.\n\nЭтой ночью погиб: {target['avatar']} {target['name']}")
        await check_victory(message)
        
        if game["phase"] != "over":
            await message.answer("🗣 **ДЕНЬ**. Обсудите, кто мафия, и проголосуйте в Mini App!")
            game["phase"] = "day"

async def check_victory(message):
    mafia = [p for p in game["players"] if p['role_key'] == "mafia" and p['status'] == "alive"]
    civilians = [p for p in game["players"] if p['role_key'] != "mafia" and p['status'] == "alive"]
    
    if not mafia:
        await message.answer("🎉 **ПОБЕДА МИРНЫХ!** Вся мафия устранена.")
        game["phase"] = "over"
    elif len(mafia) >= len(civilians):
        await message.answer("💀 **ПОБЕДА МАФИИ!** Город захвачен.")
        game["phase"] = "over"

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())