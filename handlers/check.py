from aiogram import types
from services.payment_service import check_payment
from utils.payments import get_payment, remove_payment
from utils.user_roles import set_user_role

async def check_payment_command(message: types.Message):
    record = get_payment(message.from_user.id)
    if not record:
        await message.answer("❌ У вас нет ожидающих платежей.")
        return

    payment_id = record["payment_id"]
    role = record["role"]
    if check_payment(payment_id):
        set_user_role(message.from_user.id, role)
        remove_payment(message.from_user.id)
        await message.answer(f"✅ Платёж прошёл, ваша роль обновлена на <b>{role}</b>!")
    else:
        await message.answer("⏳ Платёж ещё не завершён, попробуйте позже.")
