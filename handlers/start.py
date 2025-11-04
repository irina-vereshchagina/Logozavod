# handlers/start.py
from aiogram import types
from keyboards import get_main_keyboard
from utils.user_state import set_user_state, STATE_MENU
from utils.user_roles import set_user_role, get_user_role

# Порядок ролей для up/down
ROLE_ORDER = ["user_free", "user_basic", "user_pro", "admin"]

# Вынеси в .env при желании
SETROLE_PASSWORD = "qweqweqwe"

HELP_TEXT = (
    "❓ Формат команды:\n"
    "<code>/setrole me ПАРОЛЬ user_basic</code>\n"
    "<code>/setrole me ПАРОЛЬ up</code>\n"
    "<code>/setrole me ПАРОЛЬ down</code>"
)

async def start(message: types.Message) -> None:
    """
    Показ главного меню.
    Используется для /start и для возврата «⬅️ В меню».
    """
    user_id = message.from_user.id
    set_user_state(user_id, STATE_MENU)
    await message.answer(
        "👋 Привет! Я помогу сгенерировать логотип. Выбери действие:",
        reply_markup=get_main_keyboard()
    )

async def setrole_command(message: types.Message) -> None:
    """
    /setrole me <PASSWORD> <role|up|down>
    Примеры:
      /setrole me qweqweqwe user_basic
      /setrole me qweqweqwe up
      /setrole me qweqweqwe down
    """
    user_id = message.from_user.id
    text = (message.text or "").strip()

    parts = text.split(maxsplit=3)
    # ожидаем ровно 4 части: /setrole me PASSWORD ACTION
    if len(parts) != 4 or parts[0] != "/setrole" or parts[1] != "me":
        await message.answer(HELP_TEXT, reply_markup=get_main_keyboard())
        return

    _, _, password, action_raw = parts
    action = action_raw.strip().lower()

    if password != SETROLE_PASSWORD:
        await message.answer("❌ Неверный пароль.", reply_markup=get_main_keyboard())
        return

    current_role = get_user_role(user_id)
    try:
        cur_idx = ROLE_ORDER.index(current_role)
    except ValueError:
        # если вдруг текущая роль неизвестна — считаем как минимальную
        cur_idx = 0

    if action == "up":
        new_role = ROLE_ORDER[min(cur_idx + 1, len(ROLE_ORDER) - 1)]
    elif action == "down":
        new_role = ROLE_ORDER[max(cur_idx - 1, 0)]
    elif action in ROLE_ORDER:
        new_role = action
    else:
        await message.answer(
            "❌ Неверная роль. Допустимые: user_free, user_basic, user_pro, admin, up, down.",
            reply_markup=get_main_keyboard()
        )
        return

    set_user_role(user_id, new_role)
    await message.answer(
        f"✅ Ваша роль обновлена: <b>{new_role}</b>\n"
        f"🔁 Лимиты пересчитаны для новой роли.",
        reply_markup=get_main_keyboard()
    )
