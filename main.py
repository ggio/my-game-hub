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
    THEMES = {
        "medieval": {"name": "Средневековье", "roles": {"mafia": "Инквизитор", "civilian": "Крестьянин"}, "avatars": ["🧙‍♂️", "🛡"]},
        "star_wars": {"name": "Звездные Войны", "roles": {"mafia": "Ситх", "civilian": "Повстанец"}, "avatars": ["👽", "⚔️"]}
    }

# --- НАСТРОЙКИ ---
TOKEN = "8271945254:AAFY79RsyOuKjBe4Jposj_NsarOD0pqpaxs"
URL_APP = "https://PRODESK.github.io/my-game-hub/" 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

lobby = [] 
bot_names = ["Робот Вася", "Кибер-Петр", "Андроид Ева", "R2-D2", "Терминатор", "Валл-И"]

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    lobby.clear()
    await message.answer("🕵️‍♂️ **Mafia Online Hub**\n\nНапиши /join, чтобы войти в лобби.")

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
    
    # Сохраняем состав игроков во временную переменную для текущей игры
    random.shuffle(game_players)
    
    builder = InlineKeyboardBuilder()
    for key in THEMES.keys():
        builder.button(text=THEMES[key]['name'], callback_data=f"setup_{key}")
    
    await callback.message.answer("Выбери вселенную игры:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("setup_"))
async def finalize_game(callback: types.Callback_query):
    theme_key = callback.data.split("_")[1]
    theme = THEMES[theme_key]
    
    # Раздаем роли
    roles_pool = ["mafia", "doctor", "detective", "civilian", "civilian", "civilian"]
    random.shuffle(roles_pool)
    
    game_players = list(lobby) # Берем людей
    # Добавляем ботов до 6
    while len(game_players) < 6:
        game_players.append({"id": random.randint(1000, 9999), "name": random.choice(bot_names), "is_bot": True})
    random.shuffle(game_players)

    for i, player in enumerate(game_players):
        role_key = roles_pool[i]
        player['role'] = theme['roles'].get(role_key, "Мирный")
        player['avatar'] = random.choice(theme['avatars'])
        
        # Если это ТЫ (человек) - отправляем тебе ЛИЧНУЮ ссылку
        if not player.get('is_bot'):
            # СТРОИМ ССЫЛКУ С ДАННЫМИ
            personal_url = f"{URL_APP}?role={player['role']}&avatar={player['avatar']}&name={player['name']}"
            
            builder = ReplyKeyboardBuilder()
            builder.row(types.KeyboardButton(text="📱 ОТКРЫТЬ МОЮ КАРТУ", web_app=WebAppInfo(url=personal_url)))
            
            await bot.send_message(
                player['id'], 
                f"🎮 **ИГРА НАЧАЛАСЬ!**\n\nТвоя секретная роль: {player['role']}\nТвой аватар: {player['avatar']}\n\nНажми кнопку ниже, чтобы увидеть карту в приложении!",
                reply_markup=builder.as_markup(resize_keyboard=True)
            )

    await callback.message.answer(f"Вселенная {theme['name']} создана! Роли разданы в ЛС.")
    await callback.answer()

async def main():
    print("--- БОТ ЗАПУЩЕН И ГОТОВ К МАФИИ ---")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())