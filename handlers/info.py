from aiogram import types
from keyboards import get_main_keyboard
from utils.user_state import set_user_state, STATE_MENU
from utils.user_roles import get_user_role, get_usage, ROLE_LIMITS

async def info(message: types.Message):
    user_id = message.from_user.id
    set_user_state(user_id, STATE_MENU)

    role = get_user_role(user_id)
    usage = get_usage(user_id)
    limits = ROLE_LIMITS[role]

    g = usage["generations"]
    v = usage["vectorizations"]
    g_limit = "∞" if limits["generations"] == float("inf") else limits["generations"]
    v_limit = "∞" if limits["vectorizations"] == float("inf") else limits["vectorizations"]

    await message.answer(
        f"ℹ️ Генерация логотипов через GPT-4o + DALL·E 3.\n\n"
        f"👤 Ваша роль: <b>{role}</b>\n"
        f"🎨 Генераций: {g} / {g_limit}\n"
        f"🖼 Векторизаций: {v} / {v_limit}",
        reply_markup=get_main_keyboard()
    )
