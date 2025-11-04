from __future__ import annotations

import os
import logging
from uuid import uuid4
from decimal import Decimal, InvalidOperation

from dotenv import load_dotenv
from yookassa import Configuration, Payment

load_dotenv()

SHOP_ID = (os.getenv("YOOKASSA_SHOP_ID") or "").strip()
SECRET  = (os.getenv("YOOKASSA_SECRET_KEY") or "").strip()
if not SHOP_ID or not SECRET:
    # закомментируй на время разработки, если нет ключей
    raise RuntimeError("YOOKASSA_SHOP_ID / YOOKASSA_SECRET_KEY не заданы в .env")

Configuration.account_id = SHOP_ID
Configuration.secret_key = SECRET
Configuration.access_token = None

def _amount_str(amount: float | int | str) -> str:
    try:
        return f"{Decimal(str(amount)):.2f}"
    except (InvalidOperation, ValueError):
        raise ValueError(f"Некорректная сумма: {amount!r}")

def create_payment(amount: float | int | str, description: str, return_url: str,
                   user_id: int | str = None, role: str | None = None) -> tuple[str, str]:
    """
    Создаёт платёж в YooKassa.
    Возвращает (confirmation_url, payment_id).
    В metadata кладём user_id и роль для последующей верификации.
    """
    payload = {
        "amount": {"value": _amount_str(amount), "currency": "RUB"},
        "confirmation": {"type": "redirect", "return_url": return_url},
        "capture": True,
        "description": description,
        "metadata": {
            "env": "prod",
            "user_id": str(user_id) if user_id is not None else "",
            "role": role or "",
            "expected_amount": _amount_str(amount),
        },
    }
    try:
        payment = Payment.create(payload, idempotency_key=str(uuid4()))
        return payment.confirmation.confirmation_url, payment.id
    except Exception:
        logging.exception("YooKassa create_payment failed")
        raise

def get_payment_info(payment_id: str) -> dict:
    """
    Возвращает ключевую информацию о платеже:
    {status, amount_value, amount_currency, metadata{...}}
    """
    p = Payment.find_one(payment_id)
    info = {
        "status": getattr(p, "status", None),
        "amount_value": getattr(getattr(p, "amount", None), "value", None),
        "amount_currency": getattr(getattr(p, "amount", None), "currency", None),
        "metadata": getattr(p, "metadata", {}) or {},
    }
    return info

def is_payment_succeeded_with_amount(payment_id: str, expected_rub: str) -> bool:
    """
    True, если платёж в статусе succeeded и сумма (value, RUB) соответствует ожидаемой.
    """
    try:
        info = get_payment_info(payment_id)
    except Exception:
        logging.exception("YooKassa get_payment_info failed")
        return False

    return (
        info["status"] == "succeeded"
        and str(info["amount_value"]) == _amount_str(expected_rub)
        and (info["amount_currency"] or "RUB") == "RUB"
    )
