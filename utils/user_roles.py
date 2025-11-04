# utils/user_roles.py

import json
import os
from threading import Lock

DB_PATH = "limits_db.json"
db_lock = Lock()

ROLE_LIMITS = {
    "user_free": {"generations": 5, "vectorizations": 0},      # бесплатно
    "user_basic": {"generations": 10, "vectorizations": 1},    # 999 ₽
    "user_pro": {"generations": 25, "vectorizations": 3},      # 1999 ₽
    "admin": {"generations": float("inf"), "vectorizations": float("inf")},  # бесплатно (админы)
}

user_data = {}

def load_db():
    global user_data
    if os.path.exists(DB_PATH):
        with db_lock:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                user_data = json.load(f)
    else:
        user_data = {}

def save_db():
    with db_lock:
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)

def init_user(user_id: int):
    uid = str(user_id)
    if uid not in user_data:
        user_data[uid] = {
            "role": "user_free",
            "generations": 0,
            "vectorizations": 0,
        }
        save_db()

def get_user_role(user_id: int) -> str:
    init_user(user_id)
    return user_data[str(user_id)]["role"]

def set_user_role(user_id: int, role: str):
    init_user(user_id)
    user_data[str(user_id)]["role"] = role
    user_data[str(user_id)]["generations"] = 0  # Сброс генераций
    user_data[str(user_id)]["vectorizations"] = 0  # Сброс векторизаций
    save_db()

def get_usage(user_id: int):
    init_user(user_id)
    return user_data[str(user_id)]

def can_generate(user_id: int) -> bool:
    init_user(user_id)
    role = get_user_role(user_id)
    used = user_data[str(user_id)]["generations"]
    return used < ROLE_LIMITS[role]["generations"]

def can_vectorize(user_id: int) -> bool:
    init_user(user_id)
    role = get_user_role(user_id)
    used = user_data[str(user_id)]["vectorizations"]
    return used < ROLE_LIMITS[role]["vectorizations"]

def increment_usage(user_id: int, action: str):
    if action in ["generations", "vectorizations"]:
        init_user(user_id)
        user_data[str(user_id)][action] += 1
        save_db()
