import asyncio
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from themes import THEMES

TOKEN = "8271945254:AAFY79RsyOuKjBe4Jposj_NsarOD0pqpaxs"
URL_APP = "https://PRODESK.github.io/my-game-hub/" # Твоя ссылка на GitHub

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Переменные для хранения состояния игры
lobby = [] # Список игроков: [{"id": 123, "name": "Ivan"}, ...]

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! 🕵️‍♂️\n"
        "Добро пожаловать в Mafia Online.\n\n"
        "Напиши /join чтобы зайти в лобби.\n"
        "Когда наберется 6 человек, мы выберем тему и начнем!"
    )

@dp.message(Command("join"))
async def cmd_join(message: types.Message):
    global lobby
    # Проверяем, нет ли уже игрока в списке
    if any(player['id'] == message.from_user.id for player in lobby):
        await message.answer("Ты уже в очереди!")
        return

    lobby.append({"id": message.from_user.id, "name": message.from_user.first_name})
    count = len(lobby)
    await message.answer(f"✅ {message.from_user.first_name} в игре! (Собрано: {count}/6)")

    # Если набралось 6 — предлагаем выбрать тему
    if count == 6:
        builder = InlineKeyboardBuilder()
        for key, theme in THEMES.items():
            builder.button(text=theme['name'], callback_data=f"set_theme_{key}")
        await message.answer("🎮 Лобби заполнено! Выберите вселенную для этой игры:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("set_theme_"))
async def start_game(callback: types.Callback_query):
    global lobby
    theme_key = callback.data.split("_")[2]
    theme = THEMES[theme_key]
    
    await callback.message.answer(f"Мир выбран: {theme['name']}! Раздаю секретные роли...")
    
    # Перемешиваем игроков и роли
    random.shuffle(lobby)
    roles_pool = ["mafia", "doctor", "detective"] + ["civilian"] * (len(lobby) - 3)
    random.shuffle(roles_pool)

    for i, player in enumerate(lobby):
        role_key = roles_pool[i]
        role_name = theme['roles'][role_key]
        avatar = random.choice(theme['avatars'])
        
        # Отправляем каждому его роль в личку
        try:
            msg = f"ТВОЯ РОЛЬ: {role_name}\nТВОЙ ОБЛИК: {avatar}\n\nНикому не говори! Тссс..."
            await bot.send_message(player['id'], msg)
        except:
            await callback.message.answer(f"⚠️ {player['name']} не запустил бота, не могу отправить роль!")

    await callback.message.answer("🎭 Все роли розданы в ЛС! Открывайте Игротеку, чтобы видеть список выживших.")
    
    # Кнопка для входа в Mini App
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="📱 Открыть статус игры", web_app=WebAppInfo(url=URL_APP)))
    await callback.message.answer("Нажмите кнопку ниже:", reply_markup=builder.as_markup(resize_keyboard=True))
    
    # Очищаем лобби для новой игры после старта
    lobby = []

async def main():
    print("Мафия-бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())