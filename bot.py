import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties  # ✅ правильный импорт
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.storage.memory import MemoryStorage

from config import TELEGRAM_BOT_TOKEN
from handlers import start, info, prompt, generation, vectorize, buy
from utils.user_state import get_user_state, STATE_GENERATE, STATE_VECTORIZE, STATE_MENU
from utils.user_roles import load_db
from utils.payments import load_payments

# --- Логирование ---
logging.basicConfig(level=logging.INFO)
logging.getLogger("aiogram.event").setLevel(logging.DEBUG)

# --- Инициализация бота/диспетчера ---
defaults = DefaultBotProperties(parse_mode=ParseMode.HTML)  # ✅ правильно
bot = Bot(token=TELEGRAM_BOT_TOKEN, default=defaults)
dp = Dispatcher(storage=MemoryStorage())

# --- Вспомогательные фильтры ---
def is_generate_text(message):
    return (
        message.text
        and not message.text.startswith("/")
        and get_user_state(message.from_user.id) == STATE_GENERATE
    )

def is_vectorization_photo(message):
    return (
        message.photo
        and get_user_state(message.from_user.id) == STATE_VECTORIZE
    )

# --- Регистрация хендлеров ---
dp.message.register(start.start, CommandStart())
dp.message.register(start.setrole_command, Command(commands=["setrole"]))
dp.message.register(start.start, lambda m: m.text == "⬅️ В меню")
dp.message.register(info.info, lambda m: m.text == "ℹ️ Информация")
dp.message.register(prompt.prompt_for_idea, lambda m: m.text == "🎨 Генерация логотипа")
dp.message.register(vectorize.ask_for_image, lambda m: m.text == "🖼 Векторизация")
dp.message.register(buy.buy_menu, lambda m: m.text == "💰 Купить тариф")
dp.message.register(buy.handle_buy, lambda m: (m.text or "").startswith("Купить"))
dp.message.register(buy.confirm_payment, lambda m: (m.text or "").strip() == "✅ Я оплатил")
dp.message.register(vectorize.handle_vectorization_image, is_vectorization_photo)
dp.message.register(generation.handle_idea, is_generate_text)

# --- Фоллбек ---
@dp.message()
async def fallback_handler(message):
    state = get_user_state(message.from_user.id)
    if state == STATE_MENU:
        await message.answer("❗️Вы сейчас в главном меню. Пожалуйста, выберите действие кнопкой ниже.")
    elif state == STATE_GENERATE:
        await message.answer("❗️Ожидается текстовая идея логотипа.")
    elif state == STATE_VECTORIZE:
        await message.answer("❗️Ожидается изображение (фото) для векторизации.")
    else:
        await message.answer("❓ Непонятное состояние. Нажмите '⬅️ В меню'.")

# --- Точка входа ---
if __name__ == "__main__":
    load_db()
    load_payments()
    asyncio.run(dp.start_polling(bot))
