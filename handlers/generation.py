from aiogram import types
from aiogram.fsm.context import FSMContext
from utils.states import GenerationStates
from utils.user_state import single_user_lock, is_generating, set_generating
from services.logo_generator import generate_image
from aiogram.types import BufferedInputFile
import logging
from utils.user_roles import can_generate, increment_usage, get_usage, get_user_role, ROLE_LIMITS

from keyboards import get_back_keyboard
async def handle_idea(message: types.Message, state: FSMContext):
    state_now = await state.get_state()
    if state_now != GenerationStates.waiting_for_idea.state:
        return

    user_id = message.from_user.id

    if not message.text:
        await message.answer("❗️Ожидается текст с идеей логотипа.", reply_markup=get_back_keyboard())
        return

    if not can_generate(user_id):
        usage = get_usage(user_id)
        role = get_user_role(user_id)
        g_used = usage["generations"]
        g_total = ROLE_LIMITS[role]["generations"]

        await message.answer(
            f"❌ Вы исчерпали лимит <b>генераций логотипов</b>.\n\n"
            f"🎨 Генераций: {g_used} / {g_total}\n"
            f"ℹ️ Посмотреть лимиты можно через 'ℹ️ Информация'"
        , reply_markup=get_back_keyboard())
        return

    if is_generating(user_id):
        await message.answer("⏳ Пожалуйста, дождитесь завершения генерации логотипа.", reply_markup=get_back_keyboard())
        return

    async with single_user_lock(user_id):
        set_generating(user_id, True)
        await message.answer("Генерирую логотип, подожди немного...", reply_markup=get_back_keyboard())
        try:
            image = await generate_image(message.text)
            image.seek(0)
            input_file = BufferedInputFile(file=image.read(), filename="logo.png")
            await message.answer_photo(photo=input_file, caption="Вот логотип по твоей идее!")
            await message.answer("💡 Пришли ещё идею или нажми '⬅️ В меню'.", reply_markup=get_back_keyboard())
            increment_usage(user_id, "generations")

            # Добавляем сообщение об оставшемся лимите
            role = get_user_role(user_id)
            usage = get_usage(user_id)
            g_left = ROLE_LIMITS[role]["generations"] - usage["generations"]
            await message.answer(f"📊 Осталось генераций: {g_left}", reply_markup=get_back_keyboard())

        except Exception as e:
            logging.exception("Ошибка при генерации")
            await message.answer(f"Произошла ошибка: {e}", reply_markup=get_back_keyboard())
        finally:
            set_generating(user_id, False)