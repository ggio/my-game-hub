import asyncio
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from themes import THEMES

TOKEN = "8271945254:AAFY79RsyOuKjBe4Jposj_NsarOD0pqpaxs"
URL_APP = "https://PRODESK.github.io/my-game-hub/" 

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Глобальное состояние игры
lobby = [] 
game_players = [] # Список всех участников (люди + боты)
bot_names = ["Робот Вася", "Кибер-Петр", "Андроид Ева", "Бот Иван", "R2-D2", "Терминатор"]

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    lobby.clear()
    await message.answer("🕵️‍♂️ Мафия онлайн.\nНапиши /join для входа в лобби.")

@dp.message(Command("join"))
async def cmd_join(message: types.Message):
    if any(p['id'] == message.from_user.id for p in lobby):
        await message.answer("Ты уже в очереди!")
        return

    lobby.append({"id": message.from_user.id, "name": message.from_user.first_name, "is_bot": False})
    
    builder = InlineKeyboardBuilder()
    if len(lobby) >= 1: # Позволяем начать даже одному для теста
        builder.button(text="🤖 Добавить ботов и начать", callback_data="start_with_bots")
    
    await message.answer(f"✅ Ты в лобби! (Игроков: {len(lobby)}/6)", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "start_with_bots")
async def fill_with_bots(callback: types.Callback_query):
    global game_players
    # Добираем ботов до 6 человек
    game_players = list(lobby)
    needed = 6 - len(game_players)
    
    random_bots = random.sample(bot_names, needed)
    for name in random_bots:
        game_players.append({"id": random.randint(1000, 9999), "name": name, "is_bot": True})
    
    builder = InlineKeyboardBuilder()
    for key in THEMES.keys():
        builder.button(text=THEMES[key]['name'], callback_data=f"game_theme_{key}")
    
    await callback.message.answer("Выбери вселенную игры:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("game_theme_"))
async def setup_game(callback: types.Callback_query):
    theme_key = callback.data.split("_")[2]
    theme = THEMES[theme_key]
    
    # Раздача ролей
    random.shuffle(game_players)
    roles = ["mafia", "doctor", "detective", "civilian", "civilian", "civilian"]
    
    summary = []
    player_data_for_app = []

    for i, player in enumerate(game_players):
        role_key = roles[i]
        role_name = theme['roles'][role_key]
        avatar = random.choice(theme['avatars'])
        player['role'] = role_name
        player['avatar'] = avatar
        player['status'] = "Жив"
        
        summary.append(f"{avatar} {player['name']}: {role_name if player['is_bot'] else '???'}")
        
        # Если это живой игрок — шлем роль в ЛС
        if not player['is_bot']:
            await bot.send_message(player['id'], f"Твоя роль: {role_name}\nОблик: {avatar}")
            user_link = f"{URL_APP}?role={role_name}&avatar={avatar}&name={player['name']}"

    await callback.message.answer(f"Мир: {theme['name']}\n\nСписок участников:\n" + "\n".join(summary))
    
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="📱 Открыть статус игры", web_app=WebAppInfo(url=user_link)))
    await callback.message.answer("Игра началась! Ночь наступает...", reply_markup=builder.as_markup(resize_keyboard=True))

    # Запускаем цикл симуляции ночи
    await asyncio.sleep(3)
    await simulate_night(callback.message)

async def simulate_night(message):
    await message.answer("🌙 **НОЧЬ**. Мафия и спецроли делают ход...")
    await asyncio.sleep(4)
    
    # Честная логика бота: мафия выбирает случайную жертву (не себя)
    living_players = [p for p in game_players if p['status'] == "Жив"]
    target = random.choice(living_players)
    
    await message.answer(f"☀️ **УТРО**. Город просыпается.\n\nК сожалению, этой ночью погиб {target['avatar']} {target['name']}.")
    target['status'] = "Мертв"
    
    await message.answer("📣 Начинается обсуждение! Кто мафия? (Используйте голосовой чат)")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())