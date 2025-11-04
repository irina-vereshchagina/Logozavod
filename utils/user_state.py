import asyncio
from contextlib import asynccontextmanager

user_locks = {}
user_generation_flags = {}
user_states = {}

STATE_MENU = "menu"
STATE_GENERATE = "generate"
STATE_VECTORIZE = "vectorize"

@asynccontextmanager
async def single_user_lock(user_id: int):
    lock = user_locks.setdefault(user_id, asyncio.Lock())
    async with lock:
        yield

def is_generating(user_id):
    return user_generation_flags.get(user_id, False)

def set_generating(user_id, value: bool):
    user_generation_flags[user_id] = value

def set_user_state(user_id: int, state: str):
    user_states[user_id] = state

def get_user_state(user_id: int) -> str:
    return user_states.get(user_id, STATE_MENU)
