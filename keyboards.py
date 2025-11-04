from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard():
    """
    Главное меню — отображается после /start или при возврате кнопкой «⬅️ В меню».
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎨 Генерация логотипа")],
            [KeyboardButton(text="🖼 Векторизация")],
            [KeyboardButton(text="💰 Купить тариф")],
            [KeyboardButton(text="ℹ️ Информация")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_back_keyboard():
    """
    Клавиатура с одной кнопкой «⬅️ В меню» — используется во всех подменю.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⬅️ В меню")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_payment_keyboard():
    """
    Клавиатура для меню покупки тарифов.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Купить BASIC — 999 ₽")],
            [KeyboardButton(text="Купить PRO — 1999 ₽")],
            [KeyboardButton(text="⬅️ В меню")],
        ],
        resize_keyboard=True
    )


def get_confirm_payment_keyboard():
    """
    Клавиатура после отправки ссылки на оплату.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Я оплатил")],
            [KeyboardButton(text="⬅️ В меню")],
        ],
        resize_keyboard=True
    )
