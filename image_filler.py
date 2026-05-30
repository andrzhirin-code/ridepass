import os
import asyncio
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "ARIAL.TTF")
TEMPLATE_PATH = os.path.join(BASE_DIR, "template.png")

def generate_pdf(data: dict) -> str:
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")
    if not os.path.exists(FONT_PATH):
        raise FileNotFoundError(f"Шрифт не найден: {FONT_PATH}")

    img = Image.open(TEMPLATE_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype(FONT_PATH, size=70)

    x = 977
    y_start = 1086
    y_step = 195

    # Отладочные метки
    draw.line((0, y_start, img.width, y_start), fill="red", width=5)
    draw.line((x, 0, x, img.height), fill="blue", width=5)
    draw.ellipse([x-15, y_start-15, x+15, y_start+15], fill=(255, 0, 0))
    draw.text((x, y_start), "Тест (Тип ТС) урд", fill=(0, 0, 0), font=font, anchor="ls")

    output_path = os.path.join(BASE_DIR, f"order_{data.get('id', 'temp')}.pdf")
    img.save(output_path, "PDF", resolution=300.0)
    return output_path
