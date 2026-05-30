import os
import asyncio
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "arial.ttf")
TEMPLATE_PATH = os.path.join(BASE_DIR, "template.png")

def fill_order_template(data: dict) -> str:
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")
    if not os.path.exists(FONT_PATH):
        raise FileNotFoundError(f"Шрифт не найден: {FONT_PATH}")

    img = Image.open(TEMPLATE_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Шрифт 70px для наглядности
    font = ImageFont.truetype(FONT_PATH, size=70)

    # Координаты из твоих замеров
    x = 977
    y_start = 1086
    y_step = 195

    # ========== ОТЛАДОЧНЫЕ МЕТКИ ==========
    # Красная горизонтальная линия (Y)
    draw.line((0, y_start, img.width, y_start), fill="red", width=5)
    # Синяя вертикальная линия (X)
    draw.line((x, 0, x, img.height), fill="blue", width=5)
    # Красная точка в месте привязки текста
    draw.ellipse([x-15, y_start-15, x+15, y_start+15], fill=(255, 0, 0))
    # Тестовый текст с хвостиками (чтобы видеть посадку)
    draw.text((x, y_start), "Тест (Тип ТС) урд", fill=(0, 0, 0), font=font, anchor="ls")
    # ====================================

    # Сохраняем PDF
    output_path = os.path.join(BASE_DIR, f"order_{data.get('id', 'temp')}.pdf")
    img.save(output_path, "PDF", resolution=300.0)
    return output_path

async def fill_order_template_async(data: dict) -> str:
    return await asyncio.to_thread(fill_order_template, data)
