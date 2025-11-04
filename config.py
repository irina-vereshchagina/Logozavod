import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Приводим к булевому значению (true → True, все остальное → False)
USE_PLACEHOLDER = os.getenv("USE_PLACEHOLDER", "false").strip().lower() == "true"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
