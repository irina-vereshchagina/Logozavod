from aiogram import types
import logging

from services.payment_service import create_payment, is_payment_succeeded_with_amount, get_payment_info
from utils.user_state import set_user_state, STATE_MENU
from utils.payments import add_payment, get_payment, remove_payment
from utils.user_roles import set_user_role
from keyboards import (
    get_payment_keyboard,
    get_confirm_payment_keyboard,
    get_main_keyboard,
    get_back_keyboard,
)

log = logging.getLogger(__name__)

TARIFFS = {
    "user_basic": {"amount": 999,  "desc": "Покупка user_basic"},
    "user_pro":   {"amount": 1999, "desc": "Покупка user_pro"},
}

def _detect_tariff(text: str) -> tuple[int, str] | None:
    if "BASIC" in text:
        return TARIFFS["user_basic"]["amount"], "user_basic"
    if "PRO" in text:
        return TARIFFS["user_pro"]["amount"], "user_pro"
    return None

async def buy_menu(message: types.Message):
    set_user_state(message.from_user.id, STATE_MENU)
    await message.answer(
        "Тарифы:\n"
        "• BASIC — 10 генераций, 1 SVG\n"
        "• PRO — 20 генераций, 2 SVG\n\n"
        "Выберите тариф:",
        reply_markup=get_payment_keyboard(),
    )

async def handle_buy(message: types.Message):
    text = (message.text or "")
    detected = _detect_tariff(text)
    if not detected:
        await message.answer("❌ Такой тариф не найден", reply_markup=get_back_keyboard())
        return

    amount, role = detected
    try:
        url, payment_id = create_payment(
            amount=amount,
            description=TARIFFS[role]["desc"],
            return_url="https://t.me/Logozavod_Bot",
            user_id=message.from_user.id,
            role=role,
        )
    except Exception:
        log.exception("Ошибка создания платежа")
        await message.answer(
            "❌ Не удалось создать платёж. Проверьте настройки YooKassa и попробуйте ещё раз.",
            reply_markup=get_back_keyboard(),
        )
        return

    # сохраняем платёж (с ожидаемой суммой!) и показываем клавиатуру подтверждения
    add_payment(message.from_user.id, payment_id, role, expected_amount=str(amount))

    await message.answer(f"Для оплаты перейдите по ссылке: {url}")
    await message.answer(
        "После успешной оплаты нажмите «✅ Я оплатил».",
        reply_markup=get_confirm_payment_keyboard(),
    )

async def confirm_payment(message: types.Message):
    if (message.text or "").strip() != "✅ Я оплатил":
        return

    user_id = message.from_user.id
    data = get_payment(user_id)

    if not data:
        await message.answer(
            "❌ Активный платёж не найден.",
            reply_markup=get_main_keyboard(),
        )
        return

    payment_id = data["payment_id"]
    new_role   = data["role"]
    expected   = data["expected_amount"]

    # Жёсткая проверка: статус + сумма в рублях
    ok = is_payment_succeeded_with_amount(payment_id, expected_rub=expected)

    # (опционально) Логируем, что вернула YooKassa
    try:
        info = get_payment_info(payment_id)
        log.info("Payment info for user %s: %s", user_id, info)
    except Exception:
        pass

    if ok:
        set_user_role(user_id, new_role)
        remove_payment(user_id)
        await message.answer(
            f"✅ Оплата подтверждена. Ваша роль обновлена: <b>{new_role}</b>",
            reply_markup=get_main_keyboard(),
        )
    else:
        await message.answer(
            "⏳ Платёж ещё не подтверждён или сумма не совпадает. Проверьте оплату и попробуйте ещё раз.",
            reply_markup=get_confirm_payment_keyboard(),
        )
