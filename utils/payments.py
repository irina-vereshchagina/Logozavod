import json
import os
from threading import Lock
from typing import Dict, Optional

DB_FILE = "payments_db.json"

# Структура: { "<user_id>": { "payment_id": str, "role": str, "expected_amount": str } }
payments: Dict[str, Dict[str, str]] = {}
_lock = Lock()


def load_payments() -> None:
    """
    Загружает базу незавершённых платежей из файла.
    Вызывайте при старте бота (например, в bot.py рядом с load_db()).
    """
    global payments
    if os.path.exists(DB_FILE):
        with _lock:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                try:
                    payments = json.load(f)
                    if not isinstance(payments, dict):
                        payments = {}
                except Exception:
                    # Повреждённый файл — начнём с пустой базы
                    payments = {}
    else:
        payments = {}


def save_payments() -> None:
    """Сохраняет базу платежей в файл."""
    with _lock:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(payments, f, ensure_ascii=False, indent=2)


def add_payment(user_id: int, payment_id: str, role: str, expected_amount: str) -> None:
    """
    Регистрирует платёж для пользователя:
      - payment_id: ID платежа в YooKassa
      - role: роль, которую назначим при успешной оплате (user_basic / user_pro)
      - expected_amount: сумма, которую ожидаем получить (строка вида '999.00')
    """
    uid = str(user_id)
    with _lock:
        payments[uid] = {
            "payment_id": payment_id,
            "role": role,
            "expected_amount": expected_amount,
        }
    save_payments()


def get_payment(user_id: int) -> Optional[Dict[str, str]]:
    """
    Возвращает запись о платеже пользователя:
      { "payment_id": str, "role": str, "expected_amount": str }
    или None, если записи нет.
    """
    return payments.get(str(user_id))


def remove_payment(user_id: int) -> None:
    """Удаляет запись о платеже пользователя (после успешной обработки)."""
    uid = str(user_id)
    with _lock:
        if uid in payments:
            del payments[uid]
    save_payments()
