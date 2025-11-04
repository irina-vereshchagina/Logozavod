import os
import requests
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

USE_PLACEHOLDER = (os.getenv("USE_PLACEHOLDER", "false").strip().lower() == "true")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Если не хотим использовать OpenAI — вернём заглушку-картинку
def _placeholder_image() -> BytesIO:
    url = "https://placehold.co/1024x1024/png?text=Logo"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return BytesIO(resp.content)

async def generate_image(user_prompt: str) -> BytesIO:
    """
    Генерирует изображение логотипа.
    • Если USE_PLACEHOLDER=true — отдаёт плейсхолдер (не нужен ключ OpenAI).
    • Если используем OpenAI, то:
        - сначала уточним/улучшим промпт через новый endpoint /v1/responses,
        - затем сгенерируем изображение через Images API (gpt-image-1 или dall-e-3).
    """
    if USE_PLACEHOLDER or not OPENAI_API_KEY:
        return _placeholder_image()

    # === OpenAI 1.x синтаксис ===
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    # 1) Уточняем текстовый промпт (новый endpoint: responses.create)
    try:
        refine = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {"role": "system", "content": (
                    "Ты помогаешь создавать краткие и чёткие промпты для генерации логотипов. "
                    "Верни только одну сжатую фразу на английском без лишних комментариев."
                )},
                {"role": "user", "content": user_prompt},
            ],
        )
        refined_prompt = refine.output_text.strip()
    except Exception:
        # Если что-то пошло не так — генерируем напрямую по пользовательскому промпту
        refined_prompt = user_prompt

    # 2) Генерация изображения (Images API), НЕ через chat.completions!
    # Можно использовать "gpt-image-1" или "dall-e-3". Выберем gpt-image-1.
    img = client.images.generate(
        model="gpt-image-1",
        prompt=refined_prompt,
        n=1,
        size="1024x1024",
        # quality="standard",  # параметр не обязателен
    )

    image_url = img.data[0].url
    resp = requests.get(image_url, timeout=60)
    resp.raise_for_status()
    return BytesIO(resp.content)
