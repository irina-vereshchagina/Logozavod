import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotSettings  # ✅ заменено
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
defaults = DefaultBotSettings(parse_mode=ParseMode.HTML)  # ✅ заменено
bot = Bot(token=TELEGRAM_BOT_TOKEN, default=defaults)
dp = Dispatcher(storage=MemoryStorage())


# --- Вспомогательные фильтры ---
def is_generate_text(message):
    """Текст для генерации принимаем, только когда пользователь в состоянии GENERATE."""
    return (
        message.text
        and not message.text.startswith("/")
        and get_user_state(message.from_user.id) == STATE_GENERATE
    )


def is_vectorization_photo(message):
    """Фото для векторизации принимаем, только когда пользователь в состоянии VECTORIZE."""
    return (
        message.photo
        and get_user_state(message.from_user.id) == STATE_VECTORIZE
    )


# --- Регистрация хендлеров ---

# Базовые команды
dp.message.register(start.start, CommandStart())
dp.message.register(start.setrole_command, Command(commands=["setrole"]))

# Глобальный "Назад" — возвращает в главное меню из любого места
dp.message.register(start.start, lambda m: m.text == "⬅️ В меню")

# Информация / лимиты
dp.message.register(info.info, lambda m: m.text == "ℹ️ Информация")

# Разделы
dp.message.register(prompt.prompt_for_idea,      lambda m: m.text == "🎨 Генерация логотипа")
dp.message.register(vectorize.ask_for_image,     lambda m: m.text == "🖼 Векторизация")

# Оплата: меню, выбор тарифа, подтверждение
dp.message.register(buy.buy_menu,                lambda m: m.text == "💰 Купить тариф")
dp.message.register(buy.handle_buy,              lambda m: (m.text or "").startswith("Купить"))
dp.message.register(buy.confirm_payment,         lambda m: (m.text or "").strip() == "✅ Я оплатил")

# Обработчики по состояниям
dp.message.register(vectorize.handle_vectorization_image, is_vectorization_photo)
dp.message.register(generation.handle_idea,               is_generate_text)


# Фоллбек: подсказываем, что сейчас ожидается от пользователя
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
    load_db()         # мини-БД ролей/лимитов
    load_payments()   # подхват незавершённых платежей после рестарта
    asyncio.run(dp.start_polling(bot))
