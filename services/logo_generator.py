import os
import base64
import requests
from io import BytesIO
from dotenv import load_dotenv
from PIL import Image
from openai import OpenAI

load_dotenv()

USE_PLACEHOLDER = (os.getenv("USE_PLACEHOLDER", "false").strip().lower() == "true")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def _placeholder_image() -> BytesIO:
    url = "https://placehold.co/1024x1024/png?text=Logo"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return BytesIO(resp.content)


def _image_from_base64(base64_string: str) -> BytesIO:
    """
    Преобразует base64-строку (data:image/png;base64,...) в BytesIO с изображением JPEG
    """
    try:
        header, encoded = base64_string.split(",", 1)
        image_data = base64.b64decode(encoded)
        img = Image.open(BytesIO(image_data)).convert("RGB")  # в JPEG только RGB
        output = BytesIO()
        img.save(output, format="JPEG")
        output.seek(0)
        return output
    except Exception as e:
        print(f"❌ Ошибка при конвертации base64: {e}")
        return _placeholder_image()


async def generate_image(user_prompt: str) -> BytesIO:
    if USE_PLACEHOLDER or not OPENROUTER_API_KEY:
        return _placeholder_image()

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
        default_headers={
            "HTTP-Referer": "https://yourdomain.com",
            "X-Title": "Logozavod",
            "User-Agent": "LogozavodBot/1.0"
        }
    )

    # 1. Уточняем промпт
    try:
        refine = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[
                {"role": "system", "content": (
            "Ты помогаешь создавать промпты для генерации логотипов. "
            "Всегда уточняй, что это логотип на белом фоне, "
            "используется не более трёх цветов, "
            "в стиле flat или минималистичной текстовой иллюстрации. "
            "Ответь одной короткой фразой на английском, без пояснений и комментариев."
                )},
                {"role": "user", "content": user_prompt},
            ],
        )
        refined_prompt = refine.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ Ошибка уточнения промпта: {e}")
        refined_prompt = user_prompt

    # 2. Генерация изображения
    try:
        img_response = client.chat.completions.create(
            model="openai/gpt-5-image-mini",
            messages=[{"role": "user", "content": refined_prompt}],
            modalities=["image", "text"],
        )
        images = img_response.choices[0].message.images
        image_url = images[0].get("image_url", {}).get("url")

        if image_url.startswith("data:image"):
            return _image_from_base64(image_url)

        resp = requests.get(image_url, timeout=60)
        resp.raise_for_status()
        return BytesIO(resp.content)

    except Exception as e:
        print(f"❌ Ошибка при генерации изображения: {e}")
        return _placeholder_image()
